import os , random
from paho.mqtt import client as mqtt_client

from app.utils.tls import get_cert_and_key , get_cn_from_cert , CERT_FOLDER

CLIENT_ID = "client-001"
BROKER = "127.0.0.1"
PORT = 8883
TOPIC = "test/topic"


cert_path, key_path = get_cert_and_key()
CN = get_cn_from_cert(cert_path)
client_id = f'{CN}-{random.randint(0, 1000)}'

def on_connect(client, userdata, flags, rc):
    print("Connected with code:", rc)


def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode())

def connect_mqtt():
    client = mqtt_client.Client(
    client_id=CN,
    protocol=mqtt_client.MQTTv311
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


client = connect_mqtt()
client.loop_forever()