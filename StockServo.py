#!/usr/bin/python3

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from time import sleep

from board import SCL, SDA
import busio

# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(SCL, SDA)


pca = PCA9685(i2c)

pca.frequency = 50




# You can also specify the movement fractionally.
#fraction = 0.0
#while fraction < 1.0:
#    servo7.fraction = fraction
#    fraction += 0.01
#    time.sleep(0.03)


def main():
    try:
        servos = 0
        while servos < 4:
            servoloop = servo.Servo(pca.channels[servos])
            x=0.40
            servoloop.fraction = x
            while x < 0.70:
                x = x + 0.01
                servoloop.fraction = x
                sleep(0.05)

            while x > 0.40:
                x = x - 0.01
                servoloop.fraction = x
                sleep(0.05)
            servos = servos + 1

            if servos == 3:
                servos = 0
        pca.deinit()
    except KeyboardInterrupt:
        # clean up
        pca.deinit()
    finally:
        # clean up
        pca.deinit()


if __name__ == '__main__':
    main()