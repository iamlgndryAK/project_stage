import serial
from time import sleep
import time

ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with the COM port of your Arduino
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = 'N'
ser.stopbits = 1
sleep(3)

user = ""

last_msg = ""

while True:
    user = input()
    ser.write(user.encode("utf-8"))


