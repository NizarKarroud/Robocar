from fastapi import Depends, APIRouter
import json, asyncio
from paho.mqtt import client as mqtt_client

from app import state
from app.schemas.car import ConnectionRequest, ConnectionRequestMQTT, CommandFollowLine , CommandMovement
from app.api.deps import get_mqtt_client
from app.services.mqtt import sign_and_publish
from app.services.mqtt_handlers import open_session, close_session
from app.models.models import Command


from sqlmodel import Session
from datetime import datetime, timezone
from app.database.db import engine


router = APIRouter()

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
        client.subscribe(f"car/{payload.car_id}/telemetry")  # <--
        return {"status": "connected"}
    else:
        return {"status": "rejected"}


def _handle_command(client, payload: CommandFollowLine, topic: str, mode: str):
    payload.client_id = state.CLIENT_ID

    if payload.action == "start":
        open_session(mode)

    # enregistre la commande
    if state.active_session_id is not None:
        with Session(engine) as db:
            db.add(Command(
                session_id = state.active_session_id,
                timestamp  = datetime.now(timezone.utc).isoformat(),
                mode       = mode,
                action     = payload.action
            ))
            db.commit()

    if payload.action == "stop":
        close_session()

    sign_and_publish(
        client=client,
        topic=topic,
        payload=payload,
        SECRET_KEY=state.active_key.encode()
    )

@router.post("/control/command/follow/line")
async def control_command_follow_line(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/follow/line", "follow_line")


@router.post("/control/command/follow/wall")
async def control_command_follow_wall(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/follow/wall", "follow_wall")


@router.post("/control/command/avoid/topdown")
async def control_command_avoid_topdown(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/avoid/topdown", "avoid_topdown")


@router.post("/control/command/braitenberg")
async def control_command_braitenberg(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    _handle_command(client, payload, f"car/{state.CAR_ID}/control/command/braitenberg", "braitenberg")


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