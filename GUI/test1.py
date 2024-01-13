import paho.mqtt.client as mqtt
from time import sleep

broker_address = "192.168.43.1"
broker_port = 1883

client_id = "windoweed"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        print(client.is_connected())
    else:
        print("Failed to connect to MQTT broker")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Disconnected!!!................")
        sleep(3)
        client.connect(broker_address, broker_port)


def on_publish(client, userdata, mid):
    print("Message published")


def on_message(client, userdata, message):
    message_1 = str(message.payload.decode("utf-8"))
    print("Received message: ", message_1)


client = mqtt.Client(client_id)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(broker_address, broker_port)


topic = "topic"
builtin_message = "hello there!!"

client.publish(topic, builtin_message)


client.loop_forever()

print(client.is_connected())