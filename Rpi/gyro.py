import smbus
import time


MPU6050_ADDR = 0x68
MPU6050_REG_POWER_MGMT_1 = 0x6B
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_TEMP_OUT_H = 0x41
MPU6050_REG_GYRO_XOUT_H = 0x43


accel_scale = 16384.0  
gyro_scale = 131.0    


bus = smbus.SMBus(1)

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
    # Read a 16-bit word from the sensor register
    high = bus.read_byte_data(MPU6050_ADDR, reg)
    low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    value = (high << 8) + low

    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value

if __name__ == "__main__":
    initialize_mpu6050()

    try:
        while True:
            accel_x, temp, gyro_x = read_sensor_data()

            print(f"Acceleration X: {accel_x:.2f} g, Temperature: {temp:.2f} °C, Gyro X: {gyro_x:.2f} deg/s")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Program terminated by user.")