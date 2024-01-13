import RPi.GPIO as GPIO
import time
import paho.mqtt.publish as publish
import smbus

MPU6050_ADDR = 0x68
MPU6050_REG_POWER_MGMT_1 = 0x6B
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_TEMP_OUT_H = 0x41
MPU6050_REG_GYRO_XOUT_H = 0x43

accel_scale = 16384.0
gyro_scale = 131.0

bus = smbus.SMBus(1)

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
acceleration = "acceleration"
gyro = "gyro"

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


def initialize_mpu6050():
    bus.write_byte_data(MPU6050_ADDR, MPU6050_REG_POWER_MGMT_1, 0)

def read_sensor_data():
    accel_x_raw = read_word_2c(MPU6050_REG_ACCEL_XOUT_H)
    temp_raw = read_word_2c(MPU6050_REG_TEMP_OUT_H)
    gyro_x_raw = read_word_2c(MPU6050_REG_GYRO_XOUT_H)

    accel_x = accel_x_raw / accel_scale
    temp = (temp_raw + 521) / 340.0 
    gyro_x = gyro_x_raw / gyro_scale

    return accel_x, temp, gyro_x

def read_word_2c(reg):
    high = bus.read_byte_data(MPU6050_ADDR, reg)
    low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    value = (high << 8) + low

    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value

try:
    initialize_mpu6050()

    while True:
        distance_cm = get_distance()
        smoke_status = get_smoke()

        accel_x, temp, gyro_x = read_sensor_data()
        accel_x = f"{accel_x:.2f}"
        gyro_x = f"{gyro_x:.2f}"

        print(f"Acceleration X: {accel_x:.2f} g, Temperature: {temp:.2f} °C, Gyro X: {gyro_x:.2f} deg/s")

        print(f"Distance: {distance_cm} cm")
        

        ultrasonic_message = f"{distance_cm}"
        smoke_message = f"{smoke_status}" 
        acceleration_message = accel_x
        gyro_message = gyro_x
        

        publish.single(ultrasonic, payload=ultrasonic_message, hostname=mqtt_broker_ip)
        publish.single(smoke, payload=smoke_message, hostname=mqtt_broker_ip)
        publish.single(acceleration, payload=acceleration_message, hostname=mqtt_broker_ip)
        publish.single(gyro, payload=gyro_message, hostname=mqtt_broker_ip)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()


