from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.graphics import Color, Rectangle
from matplotlib.ticker import MultipleLocator


from kivy.animation import Animation



from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.uix.image import Image as KivyImage


import requests
import cv2
import numpy as np
import base64
from io import BytesIO
from kivy.graphics.texture import Texture

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random

import serial
from time import sleep
import time
import math

import paho.mqtt.client as mqtt

import paho.mqtt.publish as publish
import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)


# 172.20.10.3 192.168.43.159

broker_address = "172.20.10.3"
broker_port = 1883
client_id = "window2"

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

motor = "motor"
servo = "servo"
audio = "audio"
gyro = "gyro"
acceleration = "acceleration"
camera = "camera"
dust = "dust"
rain = "rain"
vibration = "vibration"
infrared = "infrared"



ultrasonic_message_1 = 0
ultrasonic_message_2 = 0
ultrasonic_message_3 = 0
ultrasonic_message_4 = 0

smoke_message_1 = 0
smoke_message_2 = 0
smoke_message_3 = 0

flame_message_1 = 0
flame_message_2 = 0
flame_message_3 = 0
flame_message_4 = 0
flame_message_5 = 0

rain_message = 0
dust_message = 0
vibration_message = 0
infrared_message = 0

acceleration_message = "0,0,0"
acceleration_message_1 = 0
acceleration_message_2 = 1
acceleration_message_3 = 2

gyro_message = "0,0,0"

x_values, y_values = [], []

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
    if value < 130:
        return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    else:
        return 100

def get_live_data():
    distance = random.uniform(0, 10)
    return distance, time.time()


class Grid(TabbedPanel):
    def __init__(self, **kwargs):
        global ultrasonic_message_1 
        super(Grid, self).__init__(**kwargs)

        self.mosquitto_button = self.ids.mosquitto_button

        try:
            self.client = mqtt.Client(client_id)
            self.start_client()
            self.mosquitto_button.background_color = [0, 1, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]

        except:
            print("Not connect to MQTT, restart require")
            self.mosquitto_button.background_color = [1, 0, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]



        self.motor_speed = 200
        self.servo_coordinate = "0,0"
        self.servo_x = 0
        self.servo_y = 0

        self.fire_status = 0
        self.headlight_status = 0

        self.label = self.ids.touch_label
        self.label.bind(on_touch_move=self.on_touch_move)

        self.ultrasonic_label_1 = self.ids.ultrasonic_label_1
        self.ultrasonic_label_2 = self.ids.ultrasonic_label_2
        self.ultrasonic_label_3 = self.ids.ultrasonic_label_3
        self.ultrasonic_label_4 = self.ids.ultrasonic_label_4

        self.ultrasonic_label_2_proximity = self.ids.ultrasonic_label_2_proximity
        self.ultrasonic_label_4_proximity = self.ids.ultrasonic_label_4_proximity

        self.smoke_label = self.ids.smoke_label        

        self.image_widget = self.ids.image_widget
        self.image_esp = self.ids.image_esp

        self.url = f'http://{broker_address}/html/cam_pic.php'
        self.url2 = f'http://172.20.10.4/cam-lo.jpg'

        self.streaming_button = self.ids.streaming_button
        self.streaming_button.background_color = [1, 0, 0, 1]
        self.streaming_button_2 = self.ids.streaming_button_2
        self.streaming_button_2.background_color = [1, 0, 0, 1]

        self.streaming_enabled = False
        self.stream_clock = None
        self.streaming_enabled_2 = False
        self.stream_clock_2 = None



        
        self.is_graphing = False
        


        Clock.schedule_interval(lambda dt: self.update_loading(), 0.1)

        self.is_playing = False


        self.image_data = None
        
    
        


    def update_image(self, dt):
    
        try:
            response = requests.get(self.url, timeout= 3)

            if response.status_code == 200:
                
                
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                
                
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                img_rgb = cv2.flip(img_rgb, 1)

                
                texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='rgb')
                texture.blit_buffer(img_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

                
                self.image_widget.texture = texture
                self.ids.image_widget_5.texture = texture
                
                
        except:
            self.stream_clock.cancel()
            self.image_widget.texture = None
            self.streaming_button.background_color = [1, 0, 0, 1]
            self.streaming_button.color = [1, 1, 1, 1]
            self.streaming_button.text = "Start the Image server"


    def update_image_2(self, dt):


        try:
            response2 = requests.get(self.url2, timeout= 3)               
            if response2.status_code == 200:
                image_array2 = np.asarray(bytearray(response2.content), dtype=np.uint8)
                img2 = cv2.imdecode(image_array2, cv2.IMREAD_COLOR)
                
                
                
                
                img_rgb2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                
                img_rgb2 = cv2.flip(img_rgb2, 1)

                
                texture2 = Texture.create(size=(img2.shape[1], img2.shape[0]), colorfmt='rgb')
                texture2.blit_buffer(img_rgb2.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

                
                
                self.ids.image_widget_2.texture = texture2
                self.image_esp.texture = texture2
                
        except:

            self.stream_clock_2.cancel()
            self.image_esp.texture = None
            self.streaming_button_2.background_color = [1, 0, 0, 1]
            self.streaming_button_2.color = [1, 1, 1, 1]
            self.streaming_button_2.text = "Start the Image server"
            

        
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


    def toggle_streaming_2(self):
        if self.streaming_enabled_2:
            self.stop_streaming_2()
        else:
            self.start_streaming_2()

    def start_streaming_2(self):
        self.streaming_enabled_2 = True
        self.streaming_button_2.background_color = [0, 1, 0, 1]
        self.streaming_button_2.color = [1, 1, 1, 1]
        self.streaming_button_2.text = "Image Server Running"
        self.stream_clock_2 = Clock.schedule_interval(self.update_image_2, 0.016)

    def stop_streaming_2(self):
        self.streaming_enabled_2 = False
        self.streaming_button_2.text = "Paused"
        if self.stream_clock_2:
            self.stream_clock_2.cancel()
            self.image_esp.texture = None



    @mainthread
    def update_loading(self):
        global ultrasonic_message_1, ultrasonic_message_2, ultrasonic_message_3, ultrasonic_message_4, smoke_message, acceleration_message_1, acceleration_message_2, acceleration_message_3

        ultrasonic_value_1 = map_value(ultrasonic_message_1, 0, 130, 0, 100)
        ultrasonic_value_2 = map_value(ultrasonic_message_2, 0, 130, 0, 100)
        ultrasonic_value_3 = map_value(ultrasonic_message_3, 0, 130, 0, 100)
        ultrasonic_value_4 = map_value(ultrasonic_message_4, 0, 130, 0, 100)


        self.ultrasonic_label_1.text = f"{int(ultrasonic_message_1)} CM"
        self.ultrasonic_label_2.text = f"{int(ultrasonic_message_2)} CM"
        self.ultrasonic_label_3.text = f"{int(ultrasonic_message_3)} CM"
        self.ultrasonic_label_4.text = f"{int(ultrasonic_message_4)} CM"
        
        self.ultrasonic_label_2_proximity.text = f"{int(ultrasonic_message_2)} CM"
        self.ultrasonic_label_4_proximity.text = f"{int(ultrasonic_message_4)} CM"

        if int(ultrasonic_value_1) > 20:
            self.ultrasonic_label_1.canvas.before.clear()  
            self.ultrasonic_label_1.canvas.before.add(Color(0, 1, 0, 0.9))  
            self.ultrasonic_label_1.canvas.before.add(Rectangle(pos=self.ultrasonic_label_1.pos, size=((ultrasonic_value_1 / 100) * self.ultrasonic_label_1.size[0], self.ultrasonic_label_1.size[1])))
        else:
            self.ultrasonic_label_1.canvas.before.clear()  
            self.ultrasonic_label_1.canvas.before.add(Color(1, 0, 0, 0.9))  
            self.ultrasonic_label_1.canvas.before.add(Rectangle(pos=self.ultrasonic_label_1.pos, size=((ultrasonic_value_1 / 100) * self.ultrasonic_label_1.size[0], self.ultrasonic_label_1.size[1])))
        
        if int(ultrasonic_value_2) > 20:
            self.ultrasonic_label_2.canvas.before.clear()  
            self.ultrasonic_label_2.canvas.before.add(Color(0, 1, 0, 0.9))  
            self.ultrasonic_label_2.canvas.before.add(Rectangle(pos=self.ultrasonic_label_2.pos, size=(self.ultrasonic_label_2.size[0], (ultrasonic_value_2 / 100) * self.ultrasonic_label_2.size[1])))
            
            self.ultrasonic_label_2_proximity.canvas.before.clear()  
            self.ultrasonic_label_2_proximity.canvas.before.add(Color(0, 1, 0, 0.9))  
            self.ultrasonic_label_2_proximity.canvas.before.add(Rectangle(pos=self.ultrasonic_label_2_proximity.pos, size=(self.ultrasonic_label_2_proximity.size[0], (ultrasonic_value_2 / 100) * self.ultrasonic_label_2_proximity.size[1])))

            
        else:
            self.ultrasonic_label_2.canvas.before.clear()  
            self.ultrasonic_label_2.canvas.before.add(Color(1, 0, 0, 0.9))  
            self.ultrasonic_label_2.canvas.before.add(Rectangle(pos=self.ultrasonic_label_2.pos, size=(self.ultrasonic_label_2.size[0], (ultrasonic_value_2 / 100) * self.ultrasonic_label_2.size[1])))

            self.ultrasonic_label_2_proximity.canvas.before.clear()  
            self.ultrasonic_label_2_proximity.canvas.before.add(Color(1, 0, 0, 0.9))  
            self.ultrasonic_label_2_proximity.canvas.before.add(Rectangle(pos=self.ultrasonic_label_2_proximity.pos, size=(self.ultrasonic_label_2_proximity.size[0], (ultrasonic_value_2 / 100) * self.ultrasonic_label_2_proximity.size[1])))
            

        if int(ultrasonic_value_3) > 20:
            self.ultrasonic_label_3.canvas.before.clear()  
            self.ultrasonic_label_3.canvas.before.add(Color(0, 1, 0, 0.9))  
            self.ultrasonic_label_3.canvas.before.add(Rectangle(pos=self.ultrasonic_label_3.pos, size=((ultrasonic_value_3 / 100) * self.ultrasonic_label_3.size[0], self.ultrasonic_label_3.size[1])))
        else:
            self.ultrasonic_label_3.canvas.before.clear()  
            self.ultrasonic_label_3.canvas.before.add(Color(1, 0, 0, 0.9))  
            self.ultrasonic_label_3.canvas.before.add(Rectangle(pos=self.ultrasonic_label_3.pos, size=((ultrasonic_value_3 / 100) * self.ultrasonic_label_3.size[0], self.ultrasonic_label_3.size[1])))

        if int(ultrasonic_value_4) > 20:
            self.ultrasonic_label_4.canvas.before.clear()  
            self.ultrasonic_label_4.canvas.before.add(Color(0, 1, 0, 0.9))  
            self.ultrasonic_label_4.canvas.before.add(Rectangle(pos=self.ultrasonic_label_4.pos, size=(self.ultrasonic_label_4.size[0], (ultrasonic_value_4 / 100) * self.ultrasonic_label_4.size[1])))

            self.ultrasonic_label_4_proximity.canvas.before.clear()  
            self.ultrasonic_label_4_proximity.canvas.before.add(Color(0, 1, 0, 0.9))  
            self.ultrasonic_label_4_proximity.canvas.before.add(Rectangle(pos=self.ultrasonic_label_4_proximity.pos, size=(self.ultrasonic_label_4_proximity.size[0], (ultrasonic_value_2 / 100) * self.ultrasonic_label_4_proximity.size[1])))

        else:
            self.ultrasonic_label_4.canvas.before.clear() 
            self.ultrasonic_label_4.canvas.before.add(Color(1, 0, 0, 0.9))  
            self.ultrasonic_label_4.canvas.before.add(Rectangle(pos=self.ultrasonic_label_4.pos, size=(self.ultrasonic_label_4.size[0], (ultrasonic_value_4 / 100) * self.ultrasonic_label_4.size[1])))

            self.ultrasonic_label_4_proximity.canvas.before.clear()  
            self.ultrasonic_label_4_proximity.canvas.before.add(Color(1, 0, 0, 0.9))  
            self.ultrasonic_label_4_proximity.canvas.before.add(Rectangle(pos=self.ultrasonic_label_4_proximity.pos, size=(self.ultrasonic_label_4_proximity.size[0], (ultrasonic_value_2 / 100) * self.ultrasonic_label_4_proximity.size[1])))

        if smoke_message_1 == "0" or smoke_message_2 == "0":
            self.smoke_label.canvas.before.clear()
            self.smoke_label.canvas.before.add(Color(0, 1, 1, 1))
            self.smoke_label.canvas.before.add(Rectangle(pos=self.smoke_label.pos, size=self.smoke_label.size))
            self.ids.smoke_text.color = (1, 0, 0, 1)
            
            if self.ids.smoke_text.text == "FIRE":
                self.ids.smoke_text.text = ""
            else:
                self.ids.smoke_text.text = "FIRE"
            

        else:
            self.smoke_label.canvas.before.clear()
            self.smoke_label.canvas.before.add(Color(0, 1, 1, 0.5))
            self.smoke_label.canvas.before.add(Rectangle(pos=self.smoke_label.pos, size=self.smoke_label.size))

        self.ids.acceleration_label.text = f"Ax={acceleration_message_1} Ay={acceleration_message_2} Az={acceleration_message_3}"

        if smoke_message_1 < 1:             # use ppm value
            smoke1 = "Normal"
        else:
            smoke1 = "Smoke Detected!"
        if smoke_message_2 < 1:
            smoke2 = "Normal"
        else:
            smoke2 = "Alcohol Detected!"
        if smoke_message_3 < 1:
            smoke3 = "Normal"
        else:
            smoke3 = "Smoke Detected!"

        self.ids.smoke_status_label.text = f"Smoke1: {smoke1}\nAlcohol1: {smoke2}\nSmoke3: {smoke3}"

        self.ids.proximity_label.text = f"{ultrasonic_message_1}CM {ultrasonic_message_2}CM {ultrasonic_message_3}CM {ultrasonic_message_4}CM"

        self.ids.dust_label.text = f"{dust_message} µg/m³"
        self.ids.rain_label.text = f"{rain_message} L/m²"
        self.ids.vibration_label.text = f"{dust_message} m/s²"
        self.ids.flame_label.text = f"{((flame_message_1 + flame_message_2 + flame_message_3 + flame_message_4 + flame_message_5)/5)}"
        

    @mainthread
    def audio_play(self):
        data = stream.read(CHUNK)
        publish.single(audio, data, hostname=broker_address)

    def toggle_audio(self):
        if self.is_playing:
            Clock.unschedule(self.audio_clock)
            self.is_playing = False
            self.ids.audio.background_color = [1, 0, 0, 1]
        else:
            self.audio_clock = Clock.schedule_interval(lambda dt: self.audio_play(), 0.01)
            self.is_playing = True
            self.ids.audio.background_color = [0, 1, 0, 1]
    


    def update_slider_label(self, *args):
        slider_value = args[1]
        slider_value = math.floor(slider_value)

        self.ids.motor_speed_label.text = "Motor Speed: " + str(slider_value)
        self.motor_speed = slider_value
        print(self.motor_speed)


    


    def graphing(self):

        ultrasonic_fig, ultrasonic_ax = plt.subplots()
        mpu_fig, mpu_ax = plt.subplots()
        smoke_fig, smoke_ax = plt.subplots()
        dust_fig, dust_ax = plt.subplots()
        

        ultrasonic_line1, = ultrasonic_ax.plot([], [], '-', label='Front', marker='')
        ultrasonic_line2, = ultrasonic_ax.plot([], [], '-', label='Left', marker='')
        ultrasonic_line3, = ultrasonic_ax.plot([], [], '-', label='Back', marker='')
        ultrasonic_line4, = ultrasonic_ax.plot([], [], '-', label='Right', marker='')

        mpu_line1, = mpu_ax.plot([], [], '-', label='Ax', marker='')
        mpu_line2, = mpu_ax.plot([], [], '-', label='Ay', marker='')
        mpu_line3, = mpu_ax.plot([], [], '-', label='Az', marker='')
        
        smoke_line1, = smoke_ax.plot([], [], '-', label='Smoke Sensor 1', marker='')
        smoke_line2, = smoke_ax.plot([], [], '-', label='Smoke Sensor 2', marker='')
        smoke_line3, = smoke_ax.plot([], [], '-', label='Smoke Sensor 3', marker='')

        dust_line1, = dust_ax.plot([], [], '-', label='Dust Sensor', marker='')


        ultrasonic_ax.set_xlabel('Time')
        ultrasonic_ax.set_ylabel('Distance')
        ultrasonic_ax.legend()

        mpu_ax.set_xlabel('Time')
        mpu_ax.set_ylabel('Acceleration')
        mpu_ax.legend()

        smoke_ax.set_xlabel('Time')
        smoke_ax.set_ylabel('Smoke PPM')
        smoke_ax.legend()

        dust_ax.set_xlabel('Time')
        dust_ax.set_ylabel('Dust ug/m3')
        dust_ax.legend()


        self.ultrasonic_plot_widget = FigureCanvasKivyAgg(figure=ultrasonic_fig)
        self.mpu_plot_widget = FigureCanvasKivyAgg(figure=mpu_fig)
        self.smoke_plot_widget = FigureCanvasKivyAgg(figure=smoke_fig)
        self.dust_plot_widget = FigureCanvasKivyAgg(figure=dust_fig)

        self.ids.live_plot_placeholder.add_widget(self.ultrasonic_plot_widget)
        self.ids.live_plot_placeholder.add_widget(self.mpu_plot_widget)
        self.ids.live_plot_placeholder.add_widget(self.smoke_plot_widget)
        self.ids.live_plot_placeholder.add_widget(self.dust_plot_widget)

        x_ultrasonic_values, ultrasonic1_values, ultrasonic2_values, ultrasonic3_values, ultrasonic4_values = [], [], [], [], []
        x_mpu_values, acceleration1_value, acceleration2_value, acceleration3_value = [], [], [], []
        x_smoke_values, smoke1_value, smoke2_value, smoke3_value = [], [], [], []
        x_dust_values, dust1_value = [], []

        update_plot_interval = 1
        
        self.ultrasonic_clock = Clock.schedule_interval(lambda dt: self.update_ultrasonic_plot(ultrasonic_ax, ultrasonic_line1, ultrasonic_line2, ultrasonic_line3, ultrasonic_line4, x_ultrasonic_values, ultrasonic1_values, ultrasonic2_values, ultrasonic3_values, ultrasonic4_values), update_plot_interval)
        self.acceleration_clock = Clock.schedule_interval(lambda dt: self.update_mpu_plot(mpu_ax, mpu_line1, mpu_line2, mpu_line3, x_mpu_values, acceleration1_value, acceleration2_value, acceleration3_value), update_plot_interval)
        self.smoke_clock = Clock.schedule_interval(lambda dt: self.update_smoke_plot(smoke_ax, smoke_line1, smoke_line2, smoke_line3, x_smoke_values, smoke1_value, smoke2_value, smoke3_value), update_plot_interval)
        self.dust_clock = Clock.schedule_interval(lambda dt: self.update_dust_plot(dust_ax, dust_line1, x_dust_values, dust1_value), update_plot_interval)



    def update_ultrasonic_plot(self, ax, line1, line2, line3, line4, x_values, y1_values, y2_values, y3_values, y4_values):
        global ultrasonic_message_1, ultrasonic_message_2, ultrasonic_message_3, ultrasonic_message_4
        current_time = time.time()
        x_values.append(current_time)
        y1_values.append(ultrasonic_message_1)  
        y2_values.append(ultrasonic_message_2)
        y3_values.append(ultrasonic_message_3)  
        y4_values.append(ultrasonic_message_4)    

        line1.set_xdata(x_values)
        line1.set_ydata(y1_values)
        line2.set_xdata(x_values)
        line2.set_ydata(y2_values)
        line3.set_xdata(x_values)
        line3.set_ydata(y3_values)
        line4.set_xdata(x_values)
        line4.set_ydata(y4_values)



        ax.relim()
        ax.autoscale_view()

        ax.legend()

        self.ultrasonic_plot_widget.draw()

    def update_mpu_plot(self, ax, line1, line2, line3, x_values, y1_values, y2_values, y3_values):
        global acceleration_message_1, acceleration_message_2, acceleration_message_3
        current_time = time.time()
        x_values.append(current_time)
        y1_values.append(acceleration_message_1)  
        y2_values.append(acceleration_message_2)
        y3_values.append(acceleration_message_3)  


        line1.set_xdata(x_values)
        line1.set_ydata(y1_values)
        line2.set_xdata(x_values)
        line2.set_ydata(y2_values)
        line3.set_xdata(x_values)
        line3.set_ydata(y3_values)


        ax.relim()
        ax.autoscale_view()

        ax.legend()

        self.mpu_plot_widget.draw()

    def update_smoke_plot(self, ax, line1, line2, line3, x_values, y1_values, y2_values, y3_values):
        global smoke_message_1, smoke_message_2, smoke_message_3
        current_time = time.time()
        x_values.append(current_time)

        y1_values.append(float(smoke_message_1)) 
        y2_values.append(float(smoke_message_2))
        y3_values.append(float(smoke_message_3))


        line1.set_xdata(x_values)
        line1.set_ydata(y1_values)
        line2.set_xdata(x_values)
        line2.set_ydata(y2_values)
        line2.set_xdata(x_values)
        line2.set_ydata(y3_values)


        ax.relim()
        ax.autoscale_view()

        ax.legend()

        self.smoke_plot_widget.draw()

    def update_dust_plot(self, ax, line1, x_values, y1_values):
        global dust_message
        current_time = time.time()
        x_values.append(current_time)

        y1_values.append(float(dust_message)) 

        line1.set_xdata(x_values)
        line1.set_ydata(y1_values)

        ax.relim()
        ax.autoscale_view()

        ax.legend()

        self.dust_plot_widget.draw()

    def toggle_graph(self):
        if self.is_graphing:
            Clock.unschedule(self.ultrasonic_clock)
            Clock.unschedule(self.acceleration_clock)
            Clock.unschedule(self.smoke_clock)
            self.ids.live_plot_placeholder.clear_widgets()
            self.is_graphing = False
            self.ids.graph.text = "Generate Graph"
            self.ids.graph.background_color = [1, 0, 0, 1]
        else:
            self.graphing()
            self.is_graphing = True
            self.ids.graph.text = "Degenerate Graph"
            self.ids.graph.background_color = [0, 1, 0, 1]
            
            
        
        

    

    def send_value(self, value):
        print(f"Sending value: {value}")
        number = str(value)

        self.client.publish(motor, number.encode("utf-8"))

    def forward_press(self, *args):
        arduino_message = f"{self.motor_speed},0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        print("forward")
        self.send_value(arduino_message)
        

        


    def forward_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)
        
    
    def backward_press(self, button_instance):
        arduino_message = f"0,{self.motor_speed},0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)
        

    def backward_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)

    def left_press(self, button_instance):
        arduino_message = f"0,0,{self.motor_speed},0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)

    def left_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)

    def right_press(self, button_instance):
        arduino_message = f"0,0,0,{self.motor_speed},{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)

    def right_release(self, button_instance):
        arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)


    def on_rot_left_button_press(self):
        
        if self.servo_x < 180:
            self.servo_x = self.servo_x + 10

            print(f"Sending numerical value: {self.servo_x}")

            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"
            arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
            self.send_value(arduino_message)

            print("Rotating")

    def on_rot_right_button_press(self):
        
        if self.servo_x > 0:
            self.servo_x = self.servo_x - 10

            print(f"Sending numerical value: {self.servo_x}")
            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"

            arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
            self.send_value(arduino_message)
            print("Rotating")

    def on_rot_down_button_press(self):
        
        if self.servo_y > 0:
            self.servo_y = self.servo_y - 10

            print(f"Sending numerical value: {self.servo_y}")
            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"

            arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
            self.send_value(arduino_message)
            print("Rotating")
    
    def on_rot_up_button_press(self):
        
        if self.servo_y < 180:
            self.servo_y = self.servo_y + 10

            print(f"Sending numerical value: {self.servo_y}")

            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"
            arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
            self.send_value(arduino_message)

            print("Rotating")

    def on_touch_move(self, touch):
        if self.label.collide_point(*touch.pos):
            sleep(0.1)
            print("Moving", touch.pos[1])

            width, height = self.label.size
            window_width, window_height = Window.size

            self.servo_x = abs(map_value((window_width - width) - touch.pos[0], 0, width - 30, 0, 180))
            self.servo_y = map_value(touch.pos[1], 0, height, 0, 180) - 30
            self.servo_coordinate = f"{self.servo_x},{self.servo_y}"
            arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"

            self.send_value(arduino_message)
            print("Rotating")

            
            print(window_height - height)

    def fire_press(self):
        self.fire_status = 1
        arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)
    
    def fire_release(self):
        self.fire_status = 0
        arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)

    def toggle_headlight(self):

        if self.headlight_status == 0:
            self.headlight_status = 1
            self.ids.headlight.background_color = [0, 1, 0, 1]
            self.ids.headlight.color = [1, 1, 1, 1]
        else:
            self.headlight_status = 0
            self.ids.headlight.background_color = [1, 0, 0, 1]
            self.ids.headlight.color = [1, 1, 1, 1]
        
        arduino_message = f"0,0,0,0,{self.servo_coordinate},{self.fire_status},{self.headlight_status}" + "\n"
        self.send_value(arduino_message)

    def on_spinner_select(self, text):
        print("Spinner option selected:", text)
        
        # Get the spinner object using its ID and print its value
        spinner_value = self.ids.my_spinner.text
        print("Spinner value:", spinner_value)
    
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

        

    def on_publish(self, client, userdata, mid):
        print("Message published")
    
    @mainthread
    def on_message(self, client, userdata, message):

        global ultrasonic_message_1, ultrasonic_message_2, ultrasonic_message_3, ultrasonic_message_4, smoke_message
        message_1 = str(message.payload.decode("utf-8"))
        

        if message.topic == ultrasonic1:
            ultrasonic_message_1 = float(message.payload.decode("utf-8"))
            print(ultrasonic_message_1)
            print(message.topic)

        if message.topic == ultrasonic2:
            ultrasonic_message_2 = float(message.payload.decode("utf-8"))
            print(ultrasonic_message_2)
            print(message.topic)

        if message.topic == ultrasonic3:
            ultrasonic_message_3 = float(message.payload.decode("utf-8"))
            print(ultrasonic_message_3)
            print(message.topic)

        if message.topic == ultrasonic4:
            ultrasonic_message_4 = float(message.payload.decode("utf-8"))
            print(ultrasonic_message_4)
            print(message.topic)
        

        if message.topic == smoke1:
            smoke_message_1 = float(message.payload.decode("utf-8"))

        if message.topic == smoke2:
            smoke_message_2 = float(message.payload.decode("utf-8"))

        if message.topic == smoke3:
            smoke_message_3 = float(message.payload.decode("utf-8"))

        if message.topic == flame1:
            flame_message_1 = float(message.payload.decode("utf-8"))

        if message.topic == flame2:
            flame_message_2 = float(message.payload.decode("utf-8"))

        if message.topic == flame3:
            flame_message_3 = float(message.payload.decode("utf-8"))

        if message.topic == flame4:
            flame_message_4 = float(message.payload.decode("utf-8"))

        if message.topic == flame5:
            flame_message_5 = float(message.payload.decode("utf-8"))
            
        if message.topic == dust:
            dust_message = float(message.payload.decode("utf-8"))

        if message.topic == rain:
            rain_message = float(message.payload.decode("utf-8"))

        if message.topic == vibration:
            vibration_message = float(message.payload.decode("utf-8"))

        if message.topic == infrared:
            infrared_message = float(message.payload.decode("utf-8"))
        
        if message.topic == acceleration:
            message = message.payload.decode("utf-8")
            numbers = message.split(',')

            acceleration_message_1 = int(numbers[0])
            acceleration_message_2 = int(numbers[1])
            acceleration_message_3 = int(numbers[2])
            print(message.topic)
        
        if message.topic == "camera":
            img_bytes = base64.b64decode(message.payload.decode("utf-8"))
            np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
            self.image_data = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)



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


        print(self.client.on_connect)
        self.client.subscribe(ultrasonic1)
        self.client.subscribe(ultrasonic2)
        self.client.subscribe(ultrasonic3)
        self.client.subscribe(ultrasonic4)
        self.client.subscribe(smoke1)
        self.client.subscribe(smoke2)
        self.client.subscribe(smoke3)
        self.client.subscribe(flame1)
        self.client.subscribe(flame2)
        self.client.subscribe(flame3)
        self.client.subscribe(flame4)
        self.client.subscribe(flame5)
        self.client.subscribe(motor)
        self.client.subscribe(camera)
        self.client.subscribe(dust)
        self.client.subscribe(rain)
        self.client.subscribe(vibration)
        self.client.subscribe(infrared)


        print("topiicccccc")

    def restart_client(self):
        try:
            global broker_address
            self.client.disconnect()
            self.client = mqtt.Client("aadil")
            broker_address = self.ids.my_spinner.text
            self.url = f'http://{broker_address}/html/cam_pic.php'
            self.start_client()
            self.mosquitto_button.background_color = [0, 1, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]

        except:
            print("Not connect to MQTT, restart require")
            self.mosquitto_button.background_color = [1, 0, 0, 1]
            self.mosquitto_button.color = [1, 1, 1, 1]


class Rooted(App):
    def build(self):
        self.fig, self.ax = plt.subplots()


        x = [1, 2, 3, 4, 5]
        y = [3, 5, 7, 2, 1]

        
        self.ax.bar(x, y)

        # Set title and labels
        self.ax.set_title('Sample Bar Chart')
        self.ax.set_xlabel('X-axis')
        self.ax.set_ylabel('Y-axis')
        return Grid()


if __name__ == "__main__":
    app = Rooted()
    app.run()
