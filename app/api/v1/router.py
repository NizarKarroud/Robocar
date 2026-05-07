from fastapi import APIRouter
from app.api.v1 import car , client , camera

v1_router = APIRouter()
v1_router.include_router(car.router, prefix="/car", tags=["car"])
v1_router.include_router(client.router, prefix="/client", tags=["client"])
v1_router.include_router(camera.router, prefix="/camera", tags=["camera"])
