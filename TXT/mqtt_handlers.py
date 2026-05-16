import json
import hmac
import hashlib
from datetime import datetime, timezone
from paho.mqtt import client as mqtt_client
import state , services
import socket

SECRET_KEY = open("/etc/robocar/.secret").read().strip().encode()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip



def canonical_json(obj) -> str:
    return json.dumps(
        obj,
        separators=(',', ':'),
        sort_keys=True
    )

def sign_and_publish(client, topic: str, SECRET_KEY: bytes, payload: dict):

    json_data = canonical_json(payload)
    print(json_data)

    signature = hmac.new(
        SECRET_KEY,
        json_data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    signed = {
        "data": payload,
        "signature": signature
    }

    client.publish(topic, canonical_json(signed))


def verify_signature(payload: dict, received_signature: str) -> bool:
    json_data = canonical_json(payload)
    print(json_data)
    expected = hmac.new(
        SECRET_KEY,
        json_data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, received_signature.strip())           


def handle_control_request(raw: dict, client: mqtt_client.Client, CAR_ID: str):


    validity = verify_signature(raw["data"], raw["signature"])
    print(validity)
    
    if not validity:
        status = "rejected" 
    else :
        state.CLIENT_ID = raw["data"]["client_id"]
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

def handle_control_camera_request(raw: dict, client: mqtt_client.Client, CAR_ID: str):

    validity = verify_signature(raw["data"], raw["signature"])
    
    if not validity:
        status = "rejected" 
    else :
        request_type = raw["data"].get("request")
        
        client_id = raw["data"].get("client_id")
        print(client_id , state.CLIENT_ID)

        if request_type == "connection" and state.CLIENT_ID == client_id :
            services.camera_stream.start()
            print("connected")
            status = "accepted"

        elif request_type == "disconnection" and state.CLIENT_ID == client_id :
            status = "disconnected"

            services.camera_stream.stop()

        else:
            status = "rejected"
        
    
    sign_and_publish(
        client=client,
        topic="car/{}/control/camera/response".format(CAR_ID),
        SECRET_KEY=SECRET_KEY,
        payload={
            "status": status,
            "car_ip" : get_local_ip() if status == "accepted" else "",
            "port" : "8765",
            "path" : "/video" if status == "accepted" else "",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
    print("done")


def handle_control_command_follow_line(raw: dict, client: mqtt_client.Client, CAR_ID: str ):
    validity = verify_signature(raw["data"], raw["signature"])

    if not validity:
        print("nope2")

        return
    client_id = raw["data"].get("client_id")

    if client_id != state.CLIENT_ID:
        print("nope")
        return

    action = raw["data"].get("action")  

    if action == "stop":
        state.command_event.set()

    elif action == "start":
        state.command_event.set()
        state.command_queue.put("follow_line")

TOPIC_HANDLERS = {
    "control/request": handle_control_request,
    "control/command/follow/line" : handle_control_command_follow_line,
    "control/camera/request" : handle_control_camera_request ,
}