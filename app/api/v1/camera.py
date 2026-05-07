from fastapi import APIRouter , Depends
import asyncio
from app.utils.tls import get_cert_and_key
from app.state import TXT_IP , CAR_ID , connection_event
from app.schemas.car import CameraRequest , CameraResponse

from paho.mqtt import client as mqtt_client
from app.api.deps import get_mqtt_client , get_db
from app.services.mqtt import sign_and_publish

router = APIRouter()


@router.post("/control/camera/request")
async def control_request(
    payload: CameraRequest,
    client: mqtt_client.Client = Depends(get_mqtt_client)
):
    
    sign_and_publish(
        client=client,
        topic=f"car/{CAR_ID}/control/camera/request",
        payload=payload,
        SECRET_KEY=payload.car_key.encode()
    )


