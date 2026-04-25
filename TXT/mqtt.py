from paho.mqtt import client as mqtt_client
import json 
from mqtt_handlers import TOPIC_HANDLERS
from tls import get_cert_and_key , get_cn_from_cert , CERT_FOLDER

CAR_ID = "TXT-001"
BROKER = "10.245.70.30"
PORT = 8883


cert_path, key_path = get_cert_and_key()
CAR_ID = get_cn_from_cert(cert_path)

def on_connect(client, userdata, flags, rc):
    print("Connected with code:", rc)
    client.subscribe(f"car/{CAR_ID}/control/request")


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
    client_id=CAR_ID,
    protocol=mqtt_client.MQTTv311
    )    
    client.tls_set(
        ca_certs=r"{}/ca.crt".format(CERT_FOLDER),
        certfile=cert_path,
        keyfile=key_path
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)

    return client

