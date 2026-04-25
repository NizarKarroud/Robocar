from fastapi import Request , HTTPException
from paho.mqtt import client as mqtt_client
from app.database.db import get_db 
from app import state
get_db = get_db

def get_mqtt_client(request: Request) -> mqtt_client.Client:
    client = state.mqtt_client
    if client is None:
        raise HTTPException(503, "MQTT not connected")
    return client

