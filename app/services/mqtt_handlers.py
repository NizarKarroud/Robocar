# app/mqtt/handlers.py
from app.schemas.car import ConnectionResponse, ConnectionStatus, CameraResponse, CameraRequestStatus
from app.models.models import RobotSession, Telemetry
from app.database.db import engine
from app import state
from sqlmodel import Session
from datetime import datetime, timezone

def handle_control_response(payload: dict):
    response = ConnectionResponse(**payload.get("data"))
    if response.status == ConnectionStatus.ACCEPTED and state.pending_key:
        state.CAR_ID = response.car_id
        state.active_key = state.pending_key
        state.pending_key = None
        state.connection_accepted = True
        state.connection_event.set()

    elif response.status in (ConnectionStatus.DISCONNECTED, ConnectionStatus.REJECTED):
        state.CAR_ID = None
        state.active_key = None
        state.connection_accepted = False
        state.connection_event.set()

def handle_control_camera_response(payload: dict):
    response = CameraResponse(**payload.get("data"))
    if response.status == CameraRequestStatus.ACCEPTED:
        state.CAMERA_STATUS = "accepted"
        state.CAMERA_URL = f"https://{response.car_ip}:{response.port}{response.path}"
        state.camera_event.set()
    elif response.status in (CameraRequestStatus.DISCONNECTED, CameraRequestStatus.REJECTED):
        state.CAMERA_STATUS = response.status.value
        state.CAMERA_URL = None
        state.camera_event.set()

def handle_telemetry(payload: dict):
    if state.active_session_id is None:
        return

    data = payload.get("data", payload)

    with Session(engine) as db:
        row = Telemetry(
            session_id = state.active_session_id,
            timestamp  = data.get("timestamp"),
            mode       = data.get("mode"),
            d_front    = data.get("sensors", {}).get("d_front"),
            d_left     = data.get("sensors", {}).get("d_left"),
            d_right    = data.get("sensors", {}).get("d_right"),
            d_back     = data.get("sensors", {}).get("d_back"),
            left_pwm   = data.get("command", {}).get("left_pwm"),
            right_pwm  = data.get("command", {}).get("right_pwm"),
        )
        db.add(row)
        db.commit()

def open_session(mode: str):
    with Session(engine) as db:
        session = RobotSession(
            mode       = mode,
            started_at = datetime.now(timezone.utc).isoformat()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        state.active_session_id = session.id

def close_session():
    if state.active_session_id is None:
        return
    with Session(engine) as db:
        session = db.get(RobotSession, state.active_session_id)
        if session:
            session.stopped_at = datetime.now(timezone.utc).isoformat()
            db.add(session)
            db.commit()
    state.active_session_id = None

TOPIC_HANDLERS = {
    "control/response"        : handle_control_response,
    "control/camera/response" : handle_control_camera_response,
    "telemetry"               : handle_telemetry,
}