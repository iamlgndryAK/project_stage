import paho.mqtt.publish as publish
import pyaudio
import wave


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100


broker_address = "172.20.10.3"
audio = "audio"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Streaming audio...")

while True:
    data = stream.read(CHUNK)
    publish.single(audio, data, hostname=broker_address)

stream.stop_stream()
stream.close()
p.terminate()
