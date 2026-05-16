from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.db import init_db 
from app.services.mqtt import connect_mqtt 
from app.api.v1.router import v1_router
from app import state
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    state.mqtt_client = connect_mqtt()
    state.mqtt_client.loop_start()
    yield
    state.mqtt_client.loop_stop()
    state.mqtt_client.disconnect()

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


