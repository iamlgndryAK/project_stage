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
from kivy.core.window import Window
from kivy.uix.image import Image as KivyImage


import requests
import cv2
import numpy as np
from io import BytesIO
from kivy.graphics.texture import Texture

import serial
from time import sleep
import time
import math

import paho.mqtt.client as mqtt

# 172.20.10.3 192.168.43.159

broker_address = "172.20.10.3"
broker_port = 1883
client_id = "window"

ultrasonic = "ultrasonic"
smoke = "smoke"
motor = "motor"
servo = "servo"

ultrasonic_message = 0
smoke_message = 0

try:
    ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with the COM port of your Arduino
    ser.baudrate = 115200
    ser.bytesize = 8
    ser.parity = 'N'
    ser.stopbits = 1
    sleep(3)
except:
    pass



# Builder.load_string("""" Paste .kv content here """)
Builder.load_file("modified.kv")


def map_value(value, in_min, in_max, out_min, out_max):
    # Map the value from the input range to the output range
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)



class Grid(TabbedPanel):
    def __init__(self, **kwargs): 
        super(Grid, self).__init__(**kwargs)

        self.mosquitto_button = self.ids.mosquitto_button
        
        self.streaming_button = self.ids.streaming_button

        try:
            self.client = mqtt.Client(client_id)
            self.start_client()
            self.mosquitto_button.background_color = [0, 1, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]

        except:
            print("Not connect to MQTT, restart require")
            self.mosquitto_button.background_color = [1, 0, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]


        self.loading_bar = self.ids.loading_bar
        self.percentage_label = self.ids.percentage_label

        self.motor_speed = 200
        self.servo_coordinate = "0,0"
        self.servo_x = 0
        self.servo_y = 0

        self.label = self.ids.touch_label
        self.label.bind(on_touch_move=self.on_touch_move)

        self.image_widget = self.ids.image_widget
        self.url = 'http://172.20.10.3/html/cam_pic.php'
        self.streaming_enabled = False
        self.stream_clock = None


        Clock.schedule_interval(lambda dt: self.update_loading(self.loading_bar, self.percentage_label), 0.1)

    def update_image(self, dt):
        response = requests.get(self.url)
        try:
            if response.status_code == 200:
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_rgb = cv2.rotate(img_rgb, cv2.ROTATE_180)

                
                texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
                texture.blit_buffer(img_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

                
                self.image_widget.texture = texture
                self.ids.image_widget_2.texture = texture
        except:
            self.stream_clock.cancel()
            self.image_widget.texture = None
            self.streaming_button.background_color = [1, 0, 0, 1]
            self.streaming_button.color = [1, 1, 1, 1]
            self.streaming_button.text = "Start the Image server"
            

        
    def toggle_streaming(self):
        if self.streaming_enabled:
            self.stop_streaming()
        else:
            self.start_streaming()

    def start_streaming(self):
        self.streaming_enabled = True
        self.streaming_button.background_color = [0, 1, 0, 1]
        self.streaming_button.color = [1, 1, 1, 1]
        self.streaming_button.text = "Image Server Running"
        self.stream_clock = Clock.schedule_interval(self.update_image, 0.016)

    def stop_streaming(self):
        self.streaming_enabled = False
        self.streaming_button.text = "Paused"
        if self.stream_clock:
            self.stream_clock.cancel()
            self.image_widget.texture = None


    @mainthread
    def update_loading(self, loading_bar, percentage_label):
        global ultrasonic_message
        data = map_value(ultrasonic_message, 0, 130, 0, 100)

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

        self.client.publish(motor, number.encode("utf-8"))

    def forward_press(self, *args):
        arduino_message = f"{self.motor_speed},0,0,0,{self.servo_coordinate}" + "\n"
        print("forward")
        self.send_value(arduino_message)
        


    def forward_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
        self.send_value(arduino_message)
    
    def backward_press(self, button_instance):
        arduino_message = f"0,{self.motor_speed},0,0,{self.servo_coordinate}" + "\n"
        self.send_value(arduino_message)

    def backward_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
        self.send_value(arduino_message)

    def left_press(self, button_instance):
        arduino_message = f"0,0,{self.motor_speed},0,{self.servo_coordinate}" + "\n"
        self.send_value(arduino_message)

    def left_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
        self.send_value(arduino_message)

    def right_press(self, button_instance):
        arduino_message = f"0,0,0,{self.motor_speed},{self.servo_coordinate}" + "\n"
        self.send_value(arduino_message)

    def right_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
        self.send_value(arduino_message)


    def on_rot_left_button_press(self):
        
        if self.servo_x < 180:
            self.servo_x = self.servo_x + 10

            print(f"Sending numerical value: {self.servo_x}")

            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"
            arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
            self.send_value(arduino_message)

            print("Rotating")

    def on_rot_right_button_press(self):
        
        if self.servo_x > 0:
            self.servo_x = self.servo_x - 10

            print(f"Sending numerical value: {self.servo_x}")
            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"

            arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
            self.send_value(arduino_message)
            print("Rotating")

    def on_rot_down_button_press(self):
        
        if self.servo_y > 0:
            self.servo_y = self.servo_y - 10

            print(f"Sending numerical value: {self.servo_y}")
            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"

            arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
            self.send_value(arduino_message)
            print("Rotating")
    
    def on_rot_up_button_press(self):
        
        if self.servo_y < 180:
            self.servo_y = self.servo_y + 10

            print(f"Sending numerical value: {self.servo_y}")

            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"
            arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"
            self.send_value(arduino_message)

            print("Rotating")

    def on_touch_move(self, touch):
        if self.label.collide_point(*touch.pos):
            sleep(0.1)
            print("Moving", touch.pos[1])

            width, height = self.label.size
            window_width, window_height = Window.size

            self.servo_x = map_value(touch.pos[0], window_width - width, window_width, 0, 180)
            self.servo_y = map_value(touch.pos[1], 0, height, 0, 180)
            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"
            arduino_message = f"0,0,0,0,{self.servo_coordinate}" + "\n"

            self.send_value(arduino_message)
            print("Rotating")

            
            print(window_height - height)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            print(client.is_connected())
        else:
            print("Failed to connect to MQTT broker")

    def on_disconnect(self, client, userdata, rc):
        print("disconnected")
        self.mosquitto_button.background_color = [1, 0, 0, 1]
        self.mosquitto_button.color = [1, 1, 1, 1]

        if rc != 0:
            print("Disconnected!!!................")
            sleep(3)
            client.connect(broker_address, broker_port)

    def on_publish(self, client, userdata, mid):
        print("Message published")

    def on_message(self, client, userdata, message):

        global ultrasonic_message, smoke_message
        message_1 = str(message.payload.decode("utf-8"))
        print("Received message: ", message_1)

        if message.topic == ultrasonic:
            ultrasonic_message = float(message.payload.decode("utf-8"))
            print(ultrasonic_message)
            print(message.topic)

        if message.topic == smoke:
            smoke_message = message.payload.decode("utf-8")
            print(smoke_message)
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
        self.client.subscribe(smoke)

    def restart_client(self):
        try:
            self.client.connect(broker_address, broker_port)
            self.mosquitto_button.background_color = [0, 1, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]

        except:
            print("Not connect to MQTT, restart require")
            self.mosquitto_button.background_color = [1, 0, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]


class Rooted(App):
    def build(self):
        return Grid()


if __name__ == "__main__":
    app = Rooted()
    app.run()
