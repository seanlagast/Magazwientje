#!/usr/bin/python3

import os
from ctypes.wintypes import RGB
import time
#from matplotlib.colors import to_rgb
import numpy as np
import cv2
import RPi.GPIO as GPIO  
import threading
import pyodbc
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
from board import SCL, SDA
import busio
# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from dotenv import load_dotenv
load_dotenv()

server = 'seansqlserverconxiondemo.database.windows.net' 
database = 'SeanSQLServer' 
username = 'seansimon' 
password = 'P@ssw0rd' 
driver = '{ODBC Driver 18 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

conn_str = "HostName=SeanTestIoTHuB.azure-devices.net;DeviceId=pcsean;SharedAccessKey=Wt2AeTXWBF6gsahS2TGy7F5DpUzucuJYz49aZkeFVyA="
#conn_str = os.getenv('connstring')
device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

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



def method_request_handler(method_request):
# Determine how to respond to the method request based on the method name
    if method_request.name == "reboot":
        payload = {"result": True, "data": "some data"} # set response payload
        status = 200 # set return status code
        print("executed method")
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        device_client.send_method_response(method_response)
        OrderMethod()
    else:
        payload = {"result": False, "data": "unknown method"} # set response payload
        status = 400 # set return status code
        print("executed unknown method: " + method_request.name)
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        device_client.send_method_response(method_response)


def storagethread(servoNumber):
    while servos < 4:
        servoproduct = servo.Servo(pca.channels[servoNumber])
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



def StartProcess():

    print('')
    print('')
    print('Start processing.')

    print('{} yellow ball(s).'.format(product1))
    for i in range(product1):
        storagethread(0)
        UpdateOrder("Product1")
        UpdateStock(1, 0, 0, 0)
        time.sleep(1)
    print('{} green ball(s).'.format(product2))
    for i in range(product2):
        storagethread(1)
        UpdateOrder("Product2")
        UpdateStock(0, 1, 0, 0)
        time.sleep(1)
    print('{} blue ball(s).'.format(product3))
    for i in range(product3):
        storagethread(2)
        UpdateOrder("Product3")
        UpdateStock(0, 0, 1, 0)
        time.sleep(1)
    print('{} red ball(s).'.format(product4))
    for i in range(product4):
        storagethread(3)
        UpdateOrder("Product4")
        UpdateStock(0, 0, 0, 1)
        time.sleep(1)

    time.sleep(1)
    print('All products are processed.')

def DeleteInProgress():
    cursor.execute("delete from dbo.Progress where OrderNumber = '{}'".format(OrderNumber))
    cnxn.commit()

def GetProgressRows():
    cursor.execute("select COUNT(*) from dbo.Progress")
    row = cursor.fetchone() 
    while row: 
        global rowcount
        rowcount = row[0]
        row = cursor.fetchone()

def UpdateStock(amount1, amount2, amount3, amount4):
    cursor.execute("update dbo.Stock set Product1 = Product1 - {}, Product2 = Product2 - {}, Product3 = Product3 - {}, Product4 = Product4 - {};".format(amount1, amount2, amount3, amount4))
    cnxn.commit()

def UpdateStatus(message):
    cursor.execute("update dbo.Orders set Status = '{}' where OrderNumber = '{}'".format(message, OrderNumber))
    cnxn.commit()

def UpdateInProgress():
    cursor.execute("update dbo.Progress set InProgress = 1 where OrderNumber = '{}'".format(OrderNumber))
    cnxn.commit()

def UpdateOrder(product):
    cursor.execute("update dbo.Progress set {} = {} - 1 where OrderNumber = '{}'".format(product, product , OrderNumber))
    cnxn.commit()


def GetStock():
    #print('stock nemen')
    cursor.execute("select * from dbo.Stock")
    row = cursor.fetchone() 
    while row:
        #print('stock nemen in while')
        global product1Stock
        global product2Stock
        global product3Stock
        global product4Stock

        product1Stock = row[0]
        product2Stock = row[1]
        product3Stock = row[2]
        product4Stock = row[3]
        row = cursor.fetchone()


def GetOrder():
    #print('order nemen')
    cursor.execute("select top 1 o.OrderNumber, o.Store, p.Product1, p.Product2, p.Product3, p.Product4, p.InProgress from dbo.Orders o inner join dbo.Progress p on o.OrderNumber = p.OrderNumber where (o.OrderNumber = p.OrderNumber) order by o.Id;") 
    row = cursor.fetchone()
    while row:
        #print('order nemen in while')
        global OrderNumber
        global store
        global product1
        global product2
        global product3
        global product4
        global InProgress

        OrderNumber = row[0]
        store = row[1]
        product1 = row[2]
        #print('{}'.format(product1))
        product2 = row[3]
        product3 = row[4]
        product4 = row[5]
        InProgress = row[6]
        row = cursor.fetchone()




def OrderMethod():
    while True:
        #print('Get Rows')
        GetProgressRows()
        if rowcount > 0:  
            #print('Get Stock')  
            GetStock()
            #print('Get Order') 
            GetOrder()
            while True:
                if InProgress == 0:
                    #print('Progress nog op 0')
                    GetStock()
                    GetOrder()
                    if product1 <= product1Stock and product2 <= product2Stock and product3 <= product3Stock and product4 <= product4Stock:
                        print('Enough stock.')
                        UpdateInProgress()
                        time.sleep(2)
                    else:
                        print('Not enough stock.')
                        time.sleep(5)
                else:
                    #print('progress niet op 1')
                    break
            #print('Status updaten')
            UpdateStatus("Order is being processed.")
            #print('Proces starten')
            StartProcess()
            #print('WrapUp')
            DeleteInProgress()
            UpdateStatus("Order is delivered.")
        else:
            print('Done.')
            print('')
            print('')
            break

def run():
    global check
    check = 0
    while True:
        if check == 0:
            print('Script execution.')
            OrderMethod()
            check = 1
        else:
            time.sleep(100)
            print('Checking for new push.')



def triggerTunnelServo():

    tunnelServo.fraction = 0.4
    sleep(1)
    tunnelServo.fraction = 0.5

def triggerSortingServo(color):

    if color == "red":
        sortingServo.fraction = 0.58
    elif color == "white":
        sortingServo.fraction = 0.42
    elif color == "yellow":
        sortingServo.fraction = 0.75
    elif color == "green":
        sortingServo.fraction = 0.24

def check_color(color):
    #IN BGR
    global colornow
    global colorcheck
    global i
    white_upper = (255, 255, 255)
    white_lower   = (62, 74, 115)
    red_upper = (200, 45, 54)
    red_lower   = (151, 45, 54)
    yellow_upper = (150, 127, 60)
    yellow_lower = (117, 103, 53)
    green_upper = (71, 107, 39)
    green_lower = (51, 69, 29)

    if color < red_upper and color > red_lower:
        colornow = "red"
        #sleep(3)
    elif color < yellow_upper and color > yellow_lower:
        colornow = "yellow"
        #sleep(3)
    elif color < green_upper and color > green_lower:
        colornow = "green"
        #sleep(3)
    elif color < white_upper and color > white_lower:
        colornow = "white"
        #sleep(3)
    else:
        i = 0
        colornow = ""
    
    if colorcheck == colornow:
        i = i + 1
    else:
        i = 0
    
    if i == 8:
        print(colornow)
        triggerSortingServo(colornow)
        triggerTunnelServo()
        i = 0

    colorcheck = colornow

def tunnelthread():
    while True:
        _, frame = cap.read()
        cx = int(240)
        cy = int(220)
        brightness = 250
        cv2.normalize(frame, frame, 0, brightness, cv2.NORM_MINMAX)
        # Pick pixel value
        pixel_center = frame[cy, cx]
        blue_value = pixel_center[0]
        green_value = pixel_center[1]
        red_value = pixel_center[2]
        det_color = (red_value, green_value, blue_value)
        check_color(det_color)
        #pixel_center_bgr = frame[cy, cx]
        #b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), 3)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)


def main():
    try:
        t1 = threading.Thread(target=tunnelthread)
        t2 = threading.Thread(target=run)
        t1.start()
        t2.start()
    except KeyboardInterrupt:
        # clean up
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
        pca.deinit()


if __name__ == '__main__':
    in1 = 24
    in2 = 23
    en = 25

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(in1,GPIO.OUT)
    GPIO.setup(in2,GPIO.OUT)
    GPIO.setup(en,GPIO.OUT)
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    p=GPIO.PWM(en,1000)
    #--------------------------------
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    i = 0
    colorcheck = ""
    colornow = ""
    p.start(13) #start conveyor
    tunnelServo.fraction = 0.5
    device_client.connect()
    print("Connected.")
    #device_client.on_message_received = message_received_handler
    device_client.on_method_request_received = method_request_handler
    main()