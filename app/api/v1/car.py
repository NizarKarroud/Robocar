
from fastapi import Depends , APIRouter
import json , asyncio
from paho.mqtt import client as mqtt_client

from app import state
from app.schemas.car import  ConnectionRequest , ConnectionRequestMQTT , CommandFollowLine
from app.api.deps import get_mqtt_client 
from app.services.mqtt import sign_and_publish

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
        client_id = state.CLIENT_ID,
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

        return {"status": "connected"}
    else:
        return {"status": "rejected"}

@router.post("/control/command/follow/line")
async def control_request(
    payload: CommandFollowLine,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):

    payload.client_id = state.CLIENT_ID
    sign_and_publish(
        client=client,
        topic=f"car/{state.CAR_ID}/control/command/follow/line",
        payload=payload,
        SECRET_KEY=state.active_key.encode()
    )

