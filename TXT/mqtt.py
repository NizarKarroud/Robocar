from paho.mqtt import client as mqtt_client
import json 
from mqtt_handlers import TOPIC_HANDLERS # type: ignore
from tls import get_cert_and_key , get_cn_from_cert , CERT_FOLDER # type: ignore

BROKER ="192.168.86.31"
PORT = 8883


cert_path, key_path , ca_file = get_cert_and_key()
CAR_ID = get_cn_from_cert(cert_path)

def on_connect(client, userdata, flags, rc):
    print("Connected with code:", rc)
    client.subscribe("car/{}/control/request".format(CAR_ID))
    client.subscribe("car/{}/control/camera/request".format(CAR_ID))
    client.subscribe("car/{}/control/command/follow/line".format(CAR_ID))

def on_message(client, userdata, message):
    topic = message.topic  
    raw = json.loads(message.payload.decode('utf-8'))
    topic_key = "/".join(topic.split("/")[2:])  

    handler = TOPIC_HANDLERS.get(topic_key)

    if handler:
        handler(raw ,client, CAR_ID )
    else:
        print("No handler for topic: {}".format(topic))

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

