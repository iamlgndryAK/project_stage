from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel

from kivy.animation import Animation



from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.clock import Clock, mainthread

import serial
from time import sleep
import time
import math

import paho.mqtt.client as mqtt


broker_address = "192.168.43.159"
broker_port = 1883
client_id = "window"

ultrasonic = "ultrasonic"
motor = "motor"
servo = "servo"

ultrasonic_message = 0

try:
    ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with the COM port of your Arduino
    ser.baudrate = 115200
    ser.bytesize = 8
    ser.parity = 'N'
    ser.stopbits = 1
    sleep(3)
except:
    pass

numerical_value = 0

# Builder.load_string("""" Paste .kv content here """)
Builder.load_file("modified.kv")


def map_value(value, in_min, in_max, out_min, out_max):
    # Map the value from the input range to the output range
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)



class Grid(TabbedPanel):
    def __init__(self, **kwargs): 
        super(Grid, self).__init__(**kwargs)

        try:
            self.client = mqtt.Client(client_id)
            self.start_client()
        except:
            quit()


        self.loading_bar = self.ids.loading_bar
        self.percentage_label = self.ids.percentage_label

        self.motor_speed = 200


        Clock.schedule_interval(lambda dt: self.update_loading(self.loading_bar, self.percentage_label), 0.1)

    @mainthread
    def update_loading(self, loading_bar, percentage_label):
        global ultrasonic_message
        data = map_value(message_builtin, 0, 130, 0, 100)

        number = data
        loading_bar.value = number

        percentage_label.text = f"{int(loading_bar.value)}"
    
    def update_slider_label(self, *args):
        slider_value = args[1]
        slider_value = math.floor(slider_value)

        self.ids.motor_speed_label.text = "Motor Speed: " + str(slider_value)
        self.motor_speed = slider_value
        print(self.motor_speed)


    


    

    def send_value(self, value):
        print(f"Sending value: {value}")
        number = str(value)

        try:
            ser.write(number.encode("utf-8"))
            print("sent")
        except:
            pass
        self.client.publish(motor, number.encode("utf-8"))

    def forward_press(self, *args):
        arduino_message = f"{self.motor_speed},0,0,0" + "\n"
        print("forward")
        self.send_value(arduino_message)
        


    def forward_release(self, button_instance):
        arduino_message = "0,0,0,0" + "\n"
        self.send_value(arduino_message)
    
    def backward_press(self, button_instance):
        arduino_message = f"0,{self.motor_speed},0,0" + "\n"
        self.send_value(arduino_message)

    def backward_release(self, button_instance):
        arduino_message = "0,0,0,0" + "\n"
        self.send_value(arduino_message)

    def left_press(self, button_instance):
        arduino_message = f"0,0,-{self.motor_speed},{self.motor_speed}" + "\n"
        self.send_value(arduino_message)

    def left_release(self, button_instance):
        arduino_message = "0,0,0,0" + "\n"
        self.send_value(arduino_message)

    def right_press(self, button_instance):
        arduino_message = f"0,0,{self.motor_speed},-{self.motor_speed}" + "\n"
        self.send_value(arduino_message)

    def right_release(self, button_instance):
        arduino_message = "0,0,0,0" + "\n"
        self.send_value(arduino_message)


    def on_rot_left_button_press(self):
        global numerical_value
        if numerical_value < 180:
            numerical_value = numerical_value + 10

            print(f"Sending numerical value: {numerical_value}")
            number = str(numerical_value) + "," + "22" + '\n'

            ser.write(number.encode("utf-8"))
            print("Rotating")

    def on_rot_right_button_press(self):
        global numerical_value
        if numerical_value > 0:
            numerical_value = numerical_value - 10

            print(f"Sending numerical value: {numerical_value}")
            number = str(numerical_value) + "," + "22" + '\n'

            ser.write(number.encode("utf-8"))
            print("Rotating")

    def on_touch_move(self, touch):
        if False:
            sleep(0.1)
            print("Moving", touch.pos[0])

            servo_1 = map_value(touch.pos[0], 0, 800, 0, 180)
            servo_2 = map_value(touch.pos[1], 0, 600, 0, 180)

            number = str(servo_1) + "," + str(servo_2) + '\n'

            ser.write(number.encode("utf-8"))
            print("Rotating")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            print(client.is_connected())
        else:
            print("Failed to connect to MQTT broker")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Disconnected!!!................")
            sleep(3)
            client.connect(broker_address, broker_port)

    def on_publish(self, client, userdata, mid):
        print("Message published")

    def on_message(self, client, userdata, message):

        global ultrasonic_message
        message_1 = str(message.payload.decode("utf-8"))
        print("Received message: ", message_1)

        if message.topic == ultrasonic:
            message_builtin = float(message.payload.decode("utf-8"))
            print(message_builtin)
            print(message.topic)


    def on_connect(self, client, userdata, flags, rc):
        global rc_status
        rc_status = rc
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print("Failed to connect to MQTT broker")

        return rc_status


    def start_client(self):
        
        self.client.on_connect = self.on_connect
        self.client.connect(broker_address, broker_port)
        self.client.on_disconnect = self.on_disconnect

        self.client.on_message = self.on_message
        self.client.loop_start()
        print("mmmmmmmm")
        
        try:
            self.client.subscribe(builtin_led_status)
        except:
            pass

        print(self.client.on_connect)
        self.client.subscribe(ultrasonic)
        self.client.subscribe(motor)

class Rooted(App):
    def build(self):
        return Grid()


if __name__ == "__main__":
    app = Rooted()
    app.run()
