#!/usr/bin/env python3
import smbus #import SMBus module of I2C 
from time import sleep, time, localtime #import 
import math
import pigpio
import rospy
from std_msgs.msg import *

#MPU6050 Registers and their Address 
PWR_MGMT_1 = 0x6B 
SMPLRT_DIV = 0x19 
CONFIG = 0x1A 
GYRO_CONFIG = 0x1B 
INT_ENABLE = 0x38 
ACCEL_XOUT_H = 0x3B 
ACCEL_YOUT_H = 0x3D 
ACCEL_ZOUT_H = 0x3F 
GYRO_XOUT_H = 0x43 
GYRO_YOUT_H = 0x45 
GYRO_ZOUT_H = 0x47
FS_SEL=131
SAVE=[]
last_servo_x=0
last_servo_y=0

def MPU_Init(bus, Device_Address):
    # write to sample rate register 
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7) # Write to power management register 
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1) #Write to Configuration register 
    bus.write_byte_data(Device_Address, CONFIG, 0) #Write to Gyro configuration register 
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24) #Write to interrupt enable register 
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(bus, addr, Device_Address):
    #Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr) 
    low = bus.read_byte_data(Device_Address, addr+1)
    #concatenate higher and lower value 
    value = ((high << 8) | low)
    #to get signed value from mpu6050 
    if(value > 32768):
        value = value - 65536 
    return value

def calibrate_sensor(bus, Device_Address):
    x_accel=0
    y_accel=0
    z_accel=0
    x_gyro=0
    y_gyro=0
    z_gyro=0
    base=[]
    #처음값은 버림
    #Read Accelerometer raw value
    acc_x = read_raw_data(bus, ACCEL_XOUT_H, Device_Address)
    acc_y = read_raw_data(bus, ACCEL_YOUT_H, Device_Address)
    acc_z = read_raw_data(bus, ACCEL_ZOUT_H, Device_Address)
    
    #Read Gyroscope raw value
    gyro_x = read_raw_data(bus, GYRO_XOUT_H, Device_Address)
    gyro_y = read_raw_data(bus, GYRO_YOUT_H, Device_Address)
    gyro_z = read_raw_data(bus, GYRO_ZOUT_H, Device_Address)
    

    for i in range(10):
        #Read Accelerometer raw value
        acc_x = read_raw_data(bus, ACCEL_XOUT_H, Device_Address)
        acc_y = read_raw_data(bus, ACCEL_YOUT_H, Device_Address)
        acc_z = read_raw_data(bus, ACCEL_ZOUT_H, Device_Address)
    
        #Read Gyroscope raw value
        gyro_x = read_raw_data(bus, GYRO_XOUT_H, Device_Address)
        gyro_y = read_raw_data(bus, GYRO_YOUT_H, Device_Address)
        gyro_z = read_raw_data(bus, GYRO_ZOUT_H, Device_Address)
        
        x_accel+=acc_x
        y_accel+=acc_y
        z_accel+=acc_z
        x_gyro+=gyro_x
        y_gyro+=gyro_y
        z_gyro+=gyro_z
        sleep(0.1)
    
    base.append(x_accel/50)
    base.append(y_accel/50)
    base.append(z_accel/50)
    base.append(x_gyro/50)
    base.append(y_gyro/50)
    base.append(z_gyro/50)

    return base

def save_last(SAVE, now_time, x, y, z, x_g, y_g, z_g):
    SAVE=[now_time, x, y, z, x_g, y_g, z_g]
    return SAVE

def main():
    print("initialize . . .")
    bus=smbus.SMBus(1)
    Device_Address=0x68
    MPU_Init(bus, Device_Address)
    base=calibrate_sensor(bus, Device_Address)
    print("init complete")
    SAVE=[time(), 0, 0 ,0 ,0 ,0 ,0]
    print("sssss")
    pub = rospy.Publisher("ServoAngle", Float64MultiArray, queue_size=10)
    print("11111")
    rospy.init_node('mpu6050', anonymous = True, disable_signals = True)
    print("22222")
    rate = rospy.Rate(0.01)

    while not rospy.is_shutdown():
        print("Hello!")
        RAD_to_DEG=180/3.141592
        #Read Accelerometer raw value
        acc_x = read_raw_data(bus, ACCEL_XOUT_H, Device_Address)
        acc_y = read_raw_data(bus, ACCEL_YOUT_H, Device_Address)
        acc_z = read_raw_data(bus, ACCEL_ZOUT_H, Device_Address)
        
        #Read Gyroscope raw value
        gyro_x = read_raw_data(bus, GYRO_XOUT_H, Device_Address)
        gyro_y = read_raw_data(bus, GYRO_YOUT_H, Device_Address)
        gyro_z = read_raw_data(bus, GYRO_ZOUT_H, Device_Address)
        now_time=time()
        gyro_x=(acc_x-base[0])/131
        gyro_y=(acc_y-base[1])/131
        gyro_z=(acc_z-base[2])/131

        accel_angle_y=math.atan(-1*acc_x/math.sqrt(math.pow(acc_y, 2)+math.pow(acc_z,2)))*RAD_to_DEG
        accel_angle_x=math.atan(acc_y/math.sqrt(math.pow(acc_x,2)+math.pow(acc_z,2)))*RAD_to_DEG
        accel_angle_z=0

        dt=(now_time-SAVE[0])/1000
        gyro_angle_x=gyro_x*dt+SAVE[1]
        gyro_angle_y=gyro_y*dt+SAVE[2]
        gyro_angle_z=gyro_z*dt+SAVE[3]
     
        u_gyro_angle_x=gyro_x*dt+SAVE[4]
        u_gyro_angle_y=gyro_y*dt+SAVE[5]
        u_gyro_angle_z=gyro_z*dt+SAVE[6]

        alpha=0.96
        #alpha=0
        angle_x=alpha*gyro_angle_x+(1-alpha)*accel_angle_x
        angle_y=alpha*gyro_angle_y+(1-alpha)*accel_angle_y
        angle_z=gyro_angle_z
        SAVE = save_last(SAVE, now_time, angle_x, angle_y, angle_z, u_gyro_angle_x, u_gyro_angle_y, u_gyro_angle_z)
        print("x= {}, y= {}".format(angle_x+2.6, angle_y-2)) # for test
        x_ang=((100/9)*(int(angle_x+2.6)))+1500
        y_ang=((100/9)*(int(angle_y-2)))+1500
        msg=Float64MultiArray()
        msg.data = [x_ang, y_ang]
        pub.publish(msg)
        rate.sleep()


if __name__=="__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
