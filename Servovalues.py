from ctypes.wintypes import RGB
from time import sleep
from matplotlib.colors import to_rgb
import numpy as np
import cv2
import RPi.GPIO as GPIO  
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
from board import SCL, SDA
import busio
# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(SCL, SDA)
# Create a simple PCA9685 class instance.
pca = PCA9685(i2c)
# You can optionally provide a finer tuned reference clock speed to improve the accuracy of the
# timing pulses. This calibration will be specific to each board and its environment. See the
# calibration.py example in the PCA9685 driver.
# pca = PCA9685(i2c, reference_clock_speed=25630710)
pca.frequency = 50
tunnelServo = servo.Servo(pca.channels[4])
sortingServo = servo.Servo(pca.channels[5])


while True:
    try:
        sleep(1)
        tunnelServo.fraction = 0.5
        sleep(1)
        tunnelServo.fraction = 0.10
    except KeyboardInterrupt:
        # clean up
        pca.deinit()
        break
