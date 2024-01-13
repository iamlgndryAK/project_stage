from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.properties import ObjectProperty
import paho.mqtt.client as mqtt
from time import sleep

broker_address = "192.168.43.1"
broker_port = 1883

client_id = "windoweed"

# Builder.load_string("""" Paste .kv content here """)
Builder.load_file("car.kv")





class Grid(Widget):
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

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

    def switch_builtin(self, instance):
        global builtin_message, last_press_time
        current_time = Clock.get_time()
        if current_time - last_press_time > debounce_interval:
            last_press_time = current_time
            if builtin_message == "0":
                builtin_message = "1"
                instance.background_color = [0, 1, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "ON"

                self.ids.builtin_label.color = [0, 1, 0, 1]
            else:
                builtin_message = "0"
                instance.background_color = [1, 0, 0, 1]
                instance.color = [1, 1, 1, 1]
                instance.text = "OFF"

                self.ids.builtin_label.color = [1, 0, 0, 1]

            self.client.publish(builtin_led_topic, builtin_message)
            print('BuiltIn pressed')
            print(self.client.is_connected())

class Root(App):
    def build(self):
        return Grid()


if __name__ == "__main__":
    app = Root()
    app.run()