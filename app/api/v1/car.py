
from fastapi import Depends , APIRouter
import json , asyncio
from paho.mqtt import client as mqtt_client

from app import state
from app.schemas.car import  ConnectionRequest , ConnectionRequestMQTT
from app.api.deps import get_mqtt_client , get_db
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
        SECRET_KEY=payload.car_key.encode()
    )
    try:
        await asyncio.wait_for(state.connection_event.wait(), timeout=15.0) 
    except asyncio.TimeoutError:
        state.pending_key = None
        return {"status": "timeout", "message": "Car did not respond"}

    if state.connection_accepted:
        client.subscribe(f"car/{payload.car_id}/map")

        return {"status": "connected"}
    else:
        return {"status": "rejected"}

