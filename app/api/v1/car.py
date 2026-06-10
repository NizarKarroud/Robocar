from fastapi import Depends, APIRouter
import json, asyncio, math
from paho.mqtt import client as mqtt_client

from app import state
from app.schemas.car import ConnectionRequest, ConnectionRequestMQTT, CommandFollowLine, CommandMovement, CommandJoystick
from app.api.deps import get_mqtt_client
from app.services.mqtt import sign_and_publish
from app.services.mqtt_handlers import open_session, close_session
from app.models.models import Command, Telemetry, RobotSession

from sqlmodel import Session, select
from datetime import datetime, timezone
from app.database.db import engine

router = APIRouter()

WHEEL_BASE = 22.6
PWM_TO_VCM = 0.0241
DT         = 0.02


def _compute_trajectory(session_id: int):
    with Session(engine) as db:
        session = db.get(RobotSession, session_id)
        rows    = db.exec(
            select(Telemetry)
            .where(Telemetry.session_id == session_id)
            .order_by(Telemetry.timestamp)
        ).all()

    if not rows:
        return None

    x, y, theta = 0.0, 0.0, 0.0
    points = [{"x": 0.0, "y": 0.0, "t": rows[0].timestamp}]

    for i in range(1, len(rows)):
        row   = rows[i]
        vl    = (row.left_pwm  or 0) * PWM_TO_VCM
        vr    = (row.right_pwm or 0) * PWM_TO_VCM
        v     = (vl + vr) / 2.0
        omega = (vr - vl) / WHEEL_BASE
        theta += omega * DT
        x     += v * math.cos(theta) * DT
        y     += v * math.sin(theta) * DT
        points.append({"x": round(x, 2), "y": round(y, 2), "t": row.timestamp})

    return {
        "session_id":   session_id,
        "mode":         session.mode if session else None,
        "started_at":   session.started_at if session else None,
        "stopped_at":   session.stopped_at if session else None,
        "total_points": len(points),
        "points":       points
    }


def _handle_command(client, payload: CommandFollowLine, topic: str, mode: str):
    payload.client_id = state.CLIENT_ID

    if payload.action == "start":
        open_session(mode)

    if state.active_session_id is not None:
        with Session(engine) as db:
            db.add(Command(
                session_id = state.active_session_id,
                timestamp  = datetime.now(timezone.utc).isoformat(),
                mode       = mode,
                action     = payload.action
            ))
            db.commit()

    closed_session_id = state.active_session_id

    if payload.action == "stop":
        close_session()
        traj = _compute_trajectory(closed_session_id)
        state.last_trajectory = traj
    else:
        traj = None

    sign_and_publish(
        client=client,
        topic=topic,
        payload=payload,
        SECRET_KEY=state.active_key.encode()
    )

    return traj


@router.post("/control/request")
async def control_request(
    payload: ConnectionRequest,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    state.pending_key = payload.car_key
    client.subscribe(f"car/{payload.car_id}/control/response")

    mqtt_payload = ConnectionRequestMQTT(
        car_id=payload.car_id,
        client_id=state.CLIENT_ID,
        timestamp=payload.timestamp
    )

    sign_and_publish(
        client=client,
        topic=f"car/{payload.car_id}/control/request",
        payload=mqtt_payload,
        SECRET_KEY=payload.car_key.strip().encode()
    )

    try:
        await asyncio.wait_for(state.connection_event.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        state.pending_key = None
        return {"status": "timeout", "message": "Car did not respond"}

    if state.connection_accepted:
        client.subscribe(f"car/{payload.car_id}/map")
        client.subscribe(f"car/{payload.car_id}/control/camera/response")
        client.subscribe(f"car/{payload.car_id}/telemetry")
        return {"status": "connected"}
    else:
        return {"status": "rejected"}


@router.post("/control/command/follow/line")
async def control_command_follow_line(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    traj = _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/follow/line", "follow_line")
    return {"status": "ok", "trajectory": traj}


@router.post("/control/command/follow/wall")
async def control_command_follow_wall(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    traj = _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/follow/wall", "follow_wall")
    return {"status": "ok", "trajectory": traj}


@router.post("/control/command/avoid/topdown")
async def control_command_avoid_topdown(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    traj = _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/avoid/topdown", "avoid_topdown")
    return {"status": "ok", "trajectory": traj}


@router.post("/control/command/braitenberg")
async def control_command_braitenberg(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    traj = _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/braitenberg", "braitenberg")
    return {"status": "ok", "trajectory": traj}


MOVEMENT_COMMANDS = {
    "move_forward", "move_backward", "strafe_right", "strafe_left",
    "rotate_cw", "rotate_ccw",
    "diagonal_front_right", "diagonal_front_left",
    "diagonal_rear_right", "diagonal_rear_left",
    "arc_right_gentle", "arc_left_gentle",
    "arc_right_sharp", "arc_left_sharp",
}

@router.post("/control/command/movement")
async def control_command_movement(
    payload: CommandMovement,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    if payload.command not in MOVEMENT_COMMANDS:
        return {"status": "error", "message": f"Unknown command: {payload.command}"}

    payload.client_id = state.CLIENT_ID

    if state.active_session_id is not None:
        with Session(engine) as db:
            db.add(Command(
                session_id = state.active_session_id,
                timestamp  = datetime.now(timezone.utc).isoformat(),
                mode       = payload.command,
                action     = "execute"
            ))
            db.commit()

    sign_and_publish(
        client=client,
        topic=f"car/{state.CAR_ID}/control/command/movement",
        payload=payload,
        SECRET_KEY=state.active_key.encode()
    )

    return {"status": "ok"}


@router.post("/control/command/joystick")
async def control_command_joystick(
    payload: CommandJoystick,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    payload.client_id = state.CLIENT_ID

    sign_and_publish(
        client=client,
        topic=f"car/{state.CAR_ID}/control/command/joystick",
        payload=payload,
        SECRET_KEY=state.active_key.encode()
    )

    return {"status": "ok"}


@router.get("/sensors")
def get_sensors():
    return state.last_sensors


@router.get("/sessions")
def get_sessions():
    with Session(engine) as db:
        sessions = db.exec(
            select(RobotSession).order_by(RobotSession.id.desc())
        ).all()
    return [
        {
            "id":         s.id,
            "mode":       s.mode,
            "started_at": s.started_at,
            "stopped_at": s.stopped_at,
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}/trajectory")
def get_trajectory(session_id: int):
    traj = _compute_trajectory(session_id)
    if not traj:
        return {"error": "no telemetry found for this session"}
    return traj