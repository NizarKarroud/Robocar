import json 
from paho.mqtt import client as mqtt_client
import hmac
import hashlib
from pydantic import BaseModel
from app.services.mqtt_handlers import TOPIC_HANDLERS
from app.schemas.signed import SignedPayload
from app.utils.tls import get_cert_and_key , get_cn_from_cert , CERT_FOLDER
from app import state

#BROKER ="192.168.50.122"
BROKER =  "192.168.137.1"
PORT = 8883


cert_path, key_path , ca_file= get_cert_and_key()
state.CLIENT_ID = get_cn_from_cert(cert_path)

def canonical_json(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(',', ':')
    )

def on_connect(client, userdata, flags, rc):
    print("Connected with code:", rc)


def on_message(client, userdata, message):
    topic = message.topic          
    payload = json.loads(message.payload)

    topic_key = "/".join(topic.split("/")[2:])  

    handler = TOPIC_HANDLERS.get(topic_key)

    if handler:
        handler(payload)
    else:
        print(f"No handler for topic: {topic}")
def connect_mqtt():
    client = mqtt_client.Client(
    client_id=state.CLIENT_ID,
    protocol=mqtt_client.MQTTv311
    )    
    client.tls_set(
        ca_certs=ca_file,
        certfile=cert_path,
        keyfile=key_path
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)

    return client


def sign_and_publish(client, topic, SECRET_KEY, payload: BaseModel):
    data_dict = payload.model_dump(mode="json", exclude_none=True)

    json_data = canonical_json(data_dict)
    print(json_data)
    
    signature = hmac.new(
        SECRET_KEY,
        json_data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    signed = {
        "data": data_dict,
        "signature": signature
    }

    client.publish(topic, canonical_json(signed))

def sub_topics(client : mqtt_client.Client , TXT):
   ...