import RPi.GPIO as GPIO
import time
import paho.mqtt.publish as publish

GPIO.setmode(GPIO.BOARD)

trigger_pin = 8
echo_pin = 12
ANALOG_PIN = 11  
DIGITAL_PIN = 13

GPIO.setup(DIGITAL_PIN, GPIO.IN)
GPIO.setup(ANALOG_PIN, GPIO.IN)
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)


mqtt_broker_ip = "172.20.10.3"

ultrasonic = "ultrasonic"
smoke = "smoke"

pulse_duration = 0
pulse_end_time = 0
pulse_start_time = 0

def read_digital():
    return GPIO.input(DIGITAL_PIN)

def read_analog():
    return GPIO.input(ANALOG_PIN)

def get_smoke():
    try:
        digital_value = read_digital()
        analog_value = read_analog()

        print(f"Digital Value: {digital_value}")
        print(f"Analog Value: {analog_value}")


    except KeyboardInterrupt:
        print("Program terminated by user.")
    
    return digital_value


def get_distance():
    global pulse_duration, pulse_end_time, pulse_start_time
    try:
        GPIO.output(trigger_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trigger_pin, GPIO.LOW)
    except:
        pass

    try:
        while GPIO.input(echo_pin) == 0:
            pulse_start_time = time.time()
        while GPIO.input(echo_pin) == 1:
            pulse_end_time = time.time()
    except:
        print("loose pins")

    pulse_duration = pulse_end_time - pulse_start_time
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

try:
    while True:
        distance_cm = get_distance()
        smoke_status = get_smoke()

        print(f"Distance: {distance_cm} cm")
        

        ultrasonic_message = f"{distance_cm}"
        smoke_message = f"{smoke_status}" 

        publish.single(ultrasonic, payload=ultrasonic_message, hostname=mqtt_broker_ip)
        publish.single(smoke, payload=smoke_message, hostname=mqtt_broker_ip)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()


