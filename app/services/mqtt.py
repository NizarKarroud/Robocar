import json , os , random
from paho.mqtt import client 
import hmac
import hashlib
from pydantic import BaseModel
import mqtt_handlers as Handler
from schemas.signed import SignedPayload
from utils.tls import get_cert_and_key , get_cn_from_cert , CERT_FOLDER


BROKER = "192.168.86.31"
PORT = 8883


cert_path, key_path = get_cert_and_key()
CLIENT_ID = get_cn_from_cert(cert_path)


def on_connect(client, userdata, flags, rc):
    print("Connected with code:", rc)


def on_message(client, userdata, message):
    topic = message.topic          
    payload = json.loads(message.payload)

    topic_key = "/".join(topic.split("/")[2:])  

    handler = Handler.TOPIC_HANDLERS.get(topic_key)

    if handler:
        handler(payload)
    else:
        print(f"No handler for topic: {topic}")
def connect_mqtt():
    client = client.Client(
    client_id=CLIENT_ID,
    protocol=client.MQTTv311
    )    
    client.tls_set(
        ca_certs=fr'{CERT_FOLDER}/ca.crt',
        certfile=cert_path,
        keyfile=key_path
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)

    return client

def sign_and_publish(client : client.Client , topic : str , SECRET_KEY : str , payload : BaseModel):
    json_data = payload.model_dump_json()
    signature = hmac.new(SECRET_KEY , json_data.encode() , hashlib.sha256).hexdigest()
    signed = SignedPayload(data=payload, signature=signature)
    client.publish(topic , signed.model_dump_json())

def sub_topics(client : client.Client , TXT):
   ...