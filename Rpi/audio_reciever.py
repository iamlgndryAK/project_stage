import serial
from time import sleep
import paho.mqtt.client as mqtt

import paho.mqtt.publish as publish
import pyaudio
import wave
import subprocess


def get_ip_address(interface):
    try:
        result = subprocess.check_output(['ifconfig', interface], universal_newlines=True)
        return subprocess.check_output(['awk', '/inet / {print $2}'], input=result, universal_newlines=True).strip()
    except subprocess.CalledProcessError as e:
        return None

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

audio_stream = pyaudio.PyAudio().open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      output=True,
                                      frames_per_buffer=CHUNK)

interface = 'wlan0'
ip_address = get_ip_address(interface)

broker_address = ip_address
broker_port = 1883
client_id = "rasp"

audio = "audio"




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
