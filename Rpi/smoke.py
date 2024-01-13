import RPi.GPIO as GPIO
import time


ANALOG_PIN = 11  
DIGITAL_PIN = 13 

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DIGITAL_PIN, GPIO.IN)
    GPIO.setup(ANALOG_PIN, GPIO.IN)

def read_digital():
    return GPIO.input(DIGITAL_PIN)

def read_analog():
    return GPIO.input(ANALOG_PIN)


if __name__ == "__main__":
    try:
        setup()
        while True:
            digital_value = read_digital()
            analog_value = read_analog()

            print(f"Digital Value: {digital_value}")
            print(f"Analog Value: {analog_value}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        GPIO.cleanup()