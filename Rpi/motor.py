import serial
from time import sleep
import paho.mqtt.client as mqtt

broker_address = "192.168.43.159"
broker_port = 1883
client_id = "rasp"

ultrasonic = "ultrasonic"
motor = "motor"
builtin_message = "hello there!!"

count = 0
port = "/dev/ttyACM0"

try:
    ser = serial.Serial(port, 115200)  # Replace 'COM3' with the COM port of your Arduino
    ser.baudrate = 115200
    ser.bytesize = 8
    ser.parity = 'N'
    ser.stopbits = 1
    sleep(3)
except serial.SerialException as e:
    print(f"Serial port connection error: {e}")
    ser = None


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(motor)

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
    global count, ser
    message_builtin = ""
    message_1 = str(message.payload.decode("utf-8"))
    if message.topic == ultrasonic:
        message_builtin = message.payload.decode("utf-8")
        print(message_builtin)
        print(message.topic)
    elif message.topic == motor:
        message_builtin = message.payload.decode("utf-8")
        if count > 20:
            ser = serial.Serial(port, 115200)  # Replace 'COM3' with the COM port of your Arduino
            ser.baudrate = 115200
            ser.bytesize = 8
            ser.parity = 'N'
            ser.stopbits = 1
            count = 0
        try:
            if ser:
                ser.write(message_builtin.encode("utf-8"))
                print("sent")
                count = count + 1
            else:
                print("Serial port not available.")
        except Exception as e:
            print(f"Error writing to serial port: {e}")


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
finally:
    if ser:
        ser.close()
        print("Serial port closed.")
