import json
import hmac
import hashlib
from datetime import datetime, timezone
from paho.mqtt import client as mqtt_client
import state
SECRET_KEY = open("/etc/robocar/.secret").read().strip().encode()


def verify_signature(payload_json: str, received_signature: str) -> bool:
    expected = hmac.new(
        SECRET_KEY,
        payload_json.encode(),         
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, received_signature)


def sign_and_publish(client: mqtt_client.Client, topic: str, SECRET_KEY: bytes, payload: dict):
    payload_json = json.dumps(payload, separators=(',', ':'))  
    signature = hmac.new(SECRET_KEY, payload_json.encode(), hashlib.sha256).hexdigest()
    signed = {"data": payload, "signature": signature}
    client.publish(topic, json.dumps(signed))                  


def handle_control_request(raw: dict, client: mqtt_client.Client, CAR_ID: str):
    payload = json.dumps(raw["data"], separators=(',', ':'))
    
    
    if not verify_signature(payload, raw["signature"]):
        status = "rejected" 
        state.CLIENT_ID = raw["data"]["client_id"]
    else :
        status = "accepted"


    sign_and_publish(
        client=client,
        topic="car/{}/control/response".format(CAR_ID),
        SECRET_KEY=SECRET_KEY,
        payload={
            "car_id": CAR_ID,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

def handle_control_command(raw: dict, client: mqtt_client.Client, CAR_ID: str):
    ...

def handle_control_camera_request(raw: dict, client: mqtt_client.Client, CAR_ID: str):
    ...

TOPIC_HANDLERS = {
    "control/request": handle_control_request,
    "control/command" : handle_control_command
}