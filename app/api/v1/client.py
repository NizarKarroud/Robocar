from fastapi import Depends , APIRouter
from app.api.deps import get_mqtt_client , get_db
router = APIRouter()


@router.get("/status")
def get_client_status():
    ...