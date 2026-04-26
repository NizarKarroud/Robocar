from  mqtt import connect_mqtt

mqtt_client = connect_mqtt()
mqtt_client.loop_forever()