from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.animation import Animation

from kivy.properties import ObjectProperty
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.clock import Clock, mainthread

import serial
from time import sleep
import time

import paho.mqtt.client as mqtt


broker_address = "192.168.43.159"
broker_port = 1883
client_id = "windoweed"

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

Builder.load_string(""" 
<Grid>
    GridLayout:
        id: main_grid
        cols: 1
        size: root.width, root.height
 

        GridLayout:
            id: top_grid
            cols: 1
            size_hint: (1, 0.3)
            Label:
                id: name_label
                text: "Vehicle Control and Monitoring Panel"
                font_size: 50
                color: 0.9608, 0.8706, 0.702, 1


        GridLayout:
            id: top_grid
            cols: 3
            size_hint: (2, 0.6)

            ProgressBar:
                id: loading_bar
                max: 100
                value: 0
                size_hint_y: None
                height: 200

            Video:
                id: video
                source: 'http://192.168.43.1:8080/video'
                state: "play"
                allow_stretch: True
                options: {"eos": "loop"}

            Label:
                id: percentage_label
                text: "P"
                font_size: 50
                color: 0.9608, 0.8706, 0.702, 1

                   


        GridLayout:
            id: control_grid
            cols: 5

            GridLayout:
                id: w1
                Scatter:
                    size: w1.size
                    rotation: 90
                    do_rotation: False
                    do_translation: False
                    Label:

                        text: ""

            GridLayout:
                id: control_grid
                cols: 1
                size_hint: (0.25, 1)

                Label:
                    id: name_label
                    text: ""

                    canvas.before:
                        Color:
                            rgba: self.background_color
                        Rectangle:
                            size: self.size
                            pos: self.pos

                    background_color: (0, 1, 0, 1)

                Label:
                    id: name_label
                    text: ""

                    canvas.before:
                        Color:
                            rgba: self.background_color
                        Rectangle:
                            size: self.size
                            pos: self.pos

                    background_color: (1, 0, 0, 1)
                Label:
                    id: name_label
                    text: ""

                    canvas.before:
                        Color:
                            rgba: self.background_color
                        Rectangle:
                            size: self.size
                            pos: self.pos

                    background_color: (0, 0, 1, 1)
                Label:
                    id: name_label
                    text: ""

                    canvas.before:
                        Color:
                            rgba: self.background_color
                        Rectangle:
                            size: self.size
                            pos: self.pos

                    background_color: (1, 1, 0, 1)

            GridLayout:
                id: control_grid
                cols: 1

                Label:
                    id: name_label
                    text: "IR Sensor"
                Label:
                    id: name_label
                    text: "proximit sensor"
                Label:
                    id: name_label
                    text: "accelerometer"
                Label:
                    id: name_label
                    text: "smoke sensor"



            GridLayout:
                id: control_grid
                cols: 3
                Label:
                    id: name_label
                    text: ""
                Button:
                    id: button
                    text: "forward"
                    on_press: root.forward_press(self)
                    on_release: root.forward_release(self)
                Label:
                    id: name_label
                    text: ""
                Button:
                    id: button
                    text: "Left"
                    on_press: root.left_press(self)
                    on_release: root.left_release(self)
                    

                    border: 2, 2, 2, 2
                    border_color: 1, 0, 0, 1
                    border_width: 2
                    border_radius: [15]
                    size_hint: (0.3, 0.1)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                Label:
                    id: name_label
                    text: ""
                Button:
                    id: button
                    text: "right"
                    on_press: root.right_press(self)
                    on_release: root.right_release(self)
                Label:
                    id: name_label
                    text: ""
                Button:
                    id: button
                    text: "backward"
                    on_press: root.backward_press(self)
                    on_release: root.backward_release(self)

            BoxLayout:
                orientation: 'vertical'
                padding: 20

                GridLayout:
                    id: control_grid
                    cols: 2

                    Button:
                        id: rot_left_button
                        text: "Rot"
                        on_release: root.on_rot_left_button_press()
                    Button:
                        id: rot_right_button
                        text: "Rot"
                        on_release: root.on_rot_right_button_press()
                BoxLayout:
                    orientation: 'vertical'
                    padding: 10

                    Button:
                        id: fire_button
                        text: "Fire"
                        background_normal: ''

                        background_color: 0, 0, 1, 1



                Label:
                    id: name_label
                    text: "Turret Control"


 """)


def map_value(value, in_min, in_max, out_min, out_max):
    # Map the value from the input range to the output range
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


class Grid(Widget):
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)


        self.client = mqtt.Client(client_id)
        self.start_client()


        self.loading_bar = self.ids.loading_bar
        self.percentage_label = self.ids.percentage_label 

        Clock.schedule_interval(lambda dt: self.update_loading(self.loading_bar, self.percentage_label), 0.1)

    @mainthread
    def update_loading(self, loading_bar, percentage_label):
        global ultrasonic_message
        data = map_value(message_builtin, 0, 130, 0, 100)

        number = data
        loading_bar.value = number

        percentage_label.text = f"{int(loading_bar.value)}"



    



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
        arduino_message = "200,0,0,0" + "\n"
        print("forward")
        self.send_value(arduino_message)
        


    def forward_release(self, button_instance):
        arduino_message = "0,0,0,0" + "\n"
        self.send_value(arduino_message)
    
    def backward_press(self, button_instance):
        arduino_message = "0,200,0,0" + "\n"
        self.send_value(arduino_message)

    def backward_release(self, button_instance):
        arduino_message = "0,0,0,0" + "\n"
        self.send_value(arduino_message)

    def left_press(self, button_instance):
        arduino_message = "0,0,100,0" + "\n"
        self.send_value(arduino_message)

    def left_release(self, button_instance):
        arduino_message = "0,0,0,0" + "\n"
        self.send_value(arduino_message)

    def right_press(self, button_instance):
        arduino_message = "0,0,0,100" + "\n"
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

class Root(App):
    def build(self):
        return Grid()


if __name__ == "__main__":
    app = Root()
    app.run()