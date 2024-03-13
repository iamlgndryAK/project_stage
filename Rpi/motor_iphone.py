import serial
from time import sleep
import paho.mqtt.client as mqtt
import subprocess
import paho.mqtt.publish as publish



def get_latest_ttyusb_port():
    try:
        
        result = subprocess.run('ls /dev/tty* | grep ttyACM', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            
            return result.stdout.strip()
        else:
            
            print("Error:", result.stderr.strip())
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def get_ip_address(interface):
    try:
        result = subprocess.check_output(['ifconfig', interface], universal_newlines=True)
        return subprocess.check_output(['awk', '/inet / {print $2}'], input=result, universal_newlines=True).strip()
    except subprocess.CalledProcessError as e:
        return None

interface = 'wlan0'
ip_address = get_ip_address(interface)

if ip_address:
    print(f"{ip_address}")
else:
    print(f"Failed to retrieve IP address for {interface}")


# 192.168.43.159 172.20.10.2
broker_address = ip_address

broker_port = 1883
client_id = "rasp"


motor = "motor"
builtin_message = "hello there!!"

ultrasonic1 = "ultrasonic/1"
ultrasonic2 = "ultrasonic/2"
ultrasonic3 = "ultrasonic/3"
ultrasonic4 = "ultrasonic/4"

smoke1 = "smoke/1"
smoke2 = "smoke/2"
smoke3 = "smoke/3"

flame1 = "flame/1"
flame2 = "flame/2"
flame3 = "flame/3"
flame4 = "flame/4"
flame5 = "flame/5"

dust = "dust"
vibration = "vibration"
rain = "rain"


count = 0
latest_ttyusb_port = get_latest_ttyusb_port()


port = latest_ttyusb_port

baud_rate = 115200

try:
    ser = serial.Serial(port, baud_rate)  # Replace 'COM3' with the COM port of your Arduino
    ser.baudrate = baud_rate
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
    global count, ser, port
    message_builtin = ""
    message_1 = str(message.payload.decode("utf-8"))
    
    if message.topic == motor:
        message_builtin = message.payload.decode("utf-8")
        if count > 20:
            ser = serial.Serial(port, baud_rate)  # Replace 'COM3' with the COM port of your Arduino
            ser.baudrate = baud_rate
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
                latest_ttyusb_port = get_latest_ttyusb_port()
                port = latest_ttyusb_port
                ser = serial.Serial(port, baud_rate)  # Replace 'COM3' with the COM port of your Arduino
                ser.baudrate = baud_rate
                ser.bytesize = 8
                ser.parity = 'N'
                ser.stopbits = 1
                count = 0
        except Exception as e:
            latest_ttyusb_port = get_latest_ttyusb_port()
            port = latest_ttyusb_port
            ser = serial.Serial(port, baud_rate)  # Replace 'COM3' with the COM port of your Arduino
            ser.baudrate = baud_rate
            ser.bytesize = 8
            ser.parity = 'N'
            ser.stopbits = 1
            count = 0




client = mqtt.Client(client_id)
client.on_connect = on_connect
try:
    client.connect(broker_address, broker_port)
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
client.on_disconnect = on_disconnect
client.on_message = on_message
client.loop_start()



print("mmmmmmmm")




try:
    while True:
        try:
            line = ser.readline().decode().strip()
            
            numbers_list = [float(num_str) for num_str in line.split(",")]
            print(numbers_list[11])

            messages = [
                {"topic": ultrasonic1, "payload": numbers_list[11]},
                {"topic": ultrasonic2, "payload": numbers_list[12]},
                {"topic": ultrasonic3, "payload": numbers_list[13]},
                {"topic": ultrasonic4, "payload": numbers_list[14]},
                {"topic": smoke1, "payload": numbers_list[8]},
                {"topic": smoke2, "payload": numbers_list[9]},
                {"topic": smoke3, "payload": numbers_list[10]},
                {"topic": flame1, "payload": numbers_list[3]},
                {"topic": flame2, "payload": numbers_list[4]},
                {"topic": flame3, "payload": numbers_list[5]},
                {"topic": flame4, "payload": numbers_list[6]},
                {"topic": flame5, "payload": numbers_list[7]},
                {"topic": rain, "payload": numbers_list[2]},
                {"topic": vibration, "payload": numbers_list[1]},
                {"topic": dust, "payload": numbers_list[0]}
            ]

            publish.multiple(messages, hostname=broker_address)

            

            
        except:
            print("Too Much")
        

        
        
except KeyboardInterrupt:
    print("Exiting due to keyboard interrupt.")
finally:
    if ser:
        ser.close()
        print("Serial port closed.")
