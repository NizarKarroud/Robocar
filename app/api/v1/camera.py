from fastapi import APIRouter , Depends
import asyncio
from app.utils.tls import get_cert_and_key
from app import state   
from app.schemas.car import CameraRequest , CameraResponse , CameraRequestStatus

from paho.mqtt import client as mqtt_client
from app.api.deps import get_mqtt_client 
from app.services.mqtt import sign_and_publish
from app import state

router = APIRouter()


@router.post("/request")
async def control_request(
    payload: CameraRequest,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    payload.client_id = state.CLIENT_ID
    sign_and_publish(
        client=client,
        topic=f"car/{state.CAR_ID}/control/camera/request",
        payload=payload,
        SECRET_KEY=state.active_key.encode()
    )

    try:
        await asyncio.wait_for(state.camera_event.wait(), timeout=10.0) 
    except asyncio.TimeoutError:
        return {"status": "timeout", "message": "Car did not respond"}

    if state.CAMERA_STATUS == CameraRequestStatus.ACCEPTED:
        return {"status": f"{CameraRequestStatus.ACCEPTED}", "message": "Camera ON" , "url" : f"{state.CAMERA_URL}"}
    
    elif state.CAMERA_STATUS == CameraRequestStatus.DISCONNECTED:
        return {"status": f"{CameraRequestStatus.DISCONNECTED}", "message": "Camera OFF" }

    elif state.CAMERA_STATUS == CameraRequestStatus.REJECTED:
        return {"status": f"{CameraRequestStatus.REJECTED}", "message": "Camera request rejected" }
