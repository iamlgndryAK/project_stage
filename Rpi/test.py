import RPi.GPIO as GPIO
import time
import paho.mqtt.publish as publish

GPIO.setmode(GPIO.BOARD)
trigger_pin = 8
echo_pin = 12
led_pin = 18  # Adjust this to the GPIO pin connected to the LED

GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)

mqtt_broker_ip = "172.20.10.2"
mqtt_topic = "ultrasonic"

distance = 0

def get_distance():
    global distance
    GPIO.output(trigger_pin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    while GPIO.input(echo_pin) == 0:
        pulse_start_time = time.time()
    while GPIO.input(echo_pin) == 1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def update_led_blink_speed(distance):
    
    min_distance = 0
    max_distance = 10
    min_sleep_time = 0.05
    max_sleep_time = 0.8

    # Map the distance to a sleep time between min_sleep_time and max_sleep_time
    sleep_time = max(min_sleep_time, min(max_sleep_time, distance / max_distance * max_sleep_time))

    if distance < 10:
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(sleep_time)
        GPIO.output(led_pin, GPIO.LOW)
    else:
        pass

try:
    while True:
        distance_cm = get_distance()
        print(f"Distance: {distance_cm} cm")

        mqtt_payload = f"{{\"distance_cm\": {distance_cm}}}"
        publish.single(mqtt_topic, payload=mqtt_payload, hostname=mqtt_broker_ip)

        update_led_blink_speed(distance_cm)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()
