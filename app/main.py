from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.db import init_db , get_car_status
from services.mqtt import connect_mqtt , CLIENT_ID , sign_and_publish
from schemas.car import  ConnectionRequest
import json , asyncio
import state

client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    init_db()
    client = connect_mqtt()
    client.loop_start()
    yield
    client.loop_stop()
    client.disconnect()

app = FastAPI(lifespan=lifespan)

@app.post("/car/control/request")
async def request_control(request: ConnectionRequest):
    state.pending_key = request.car_key
    client.subscribe(f"car/{request.car_id}/control/response")
    sign_and_publish(
        client=client,
        topic=f"car/{request.car_id}/control/request",
        payload=request,
        SECRET_KEY=request.car_key.encode()
    )
    try:
        await asyncio.wait_for(state.connection_event.wait(), timeout=15.0) 
    except asyncio.TimeoutError:
        state.pending_key = None
        return {"status": "timeout", "message": "Car did not respond"}

    if state.connection_accepted:
        return {"status": "connected"}
    else:
        return {"status": "rejected"}
    

@app.get("/car/{car_id}/status")
def get_status(car_id : str):
    ...