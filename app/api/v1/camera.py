from fastapi import APIRouter , Depends
import asyncio

import httpx
from fastapi.responses import StreamingResponse


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
        return {"status": CameraRequestStatus.ACCEPTED.value, "message": "Camera ON" , "url" : f"{state.CAMERA_URL}"}
    
    elif state.CAMERA_STATUS == CameraRequestStatus.DISCONNECTED:
        return {"status": CameraRequestStatus.DISCONNECTED.value, "message": "Camera OFF" }

    elif state.CAMERA_STATUS == CameraRequestStatus.REJECTED:
        return {"status": CameraRequestStatus.REJECTED.value, "message": "Camera request rejected" }


@router.get("/stream")
async def camera_stream():
    cert_path, key_path, ca_file = get_cert_and_key()
    print(state.CAMERA_URL)
    async def generate():
        async with httpx.AsyncClient(
            cert=(cert_path, key_path),
            verify=False
        ) as client:
            async with client.stream("GET", state.CAMERA_URL) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )