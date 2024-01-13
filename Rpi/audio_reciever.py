import serial
from time import sleep
import paho.mqtt.client as mqtt

import paho.mqtt.publish as publish
import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

audio_stream = pyaudio.PyAudio().open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      output=True,
                                      frames_per_buffer=CHUNK)

broker_address = "172.20.10.3"
broker_port = 1883
client_id = "rasp"

audio = "audio"

count = 0
port = "/dev/ttyACM0"



def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(audio)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Disconnected!!!................")
        sleep(3)
        try:
            client.connect(broker_address, broker_port)
        except Exception as e:
            print(f"Failed to reconnect to MQTT broker: {e}")

def on_publish(client, userdata, mid):
    print("Message published")

def on_message(client, userdata, message):
    if message.topic == audio:
        audio_stream.write(message.payload)


client = mqtt.Client(client_id)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

try:
    client.connect(broker_address, broker_port)
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")

print("mmmmmmmm")

client.loop_forever()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting due to keyboard interrupt.")
