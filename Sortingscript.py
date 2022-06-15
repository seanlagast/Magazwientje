#!/usr/bin/python3

import os
from ctypes.wintypes import RGB
from time import sleep
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
from azure.iot.device import IoTHubDeviceClient
from azure.iot.device import MethodResponse
from dotenv import load_dotenv
load_dotenv()

#Verbind met database
server = 'seansqlserverconxiondemo.database.windows.net' 
database = 'SeanSQLServer'
username = 'seansimon'
password = 'P@ssw0rd'
driver = 'FreeTDS'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password+';TDS_Version=8.0')
cursor = cnxn.cursor()

#Verbind met Azure
conn_str = "HostName=FactoryHubDemo.azure-devices.net;DeviceId=PcSean;SharedAccessKey=08/vxUJIvWaANQrBRFSIefdNKyP+ykAnEtdNO/UuPVs="
device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

#Opzetten adafruit connectie
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50
tunnelServo = servo.Servo(pca.channels[4])
sortingServo = servo.Servo(pca.channels[5])


#Motor config
in1dc1 = 23
enadc1 = 24

in1dc2 = 27
in2dc2 = 17
enadc2 = 22

in3dc3 = 6
enbdc3 = 26


GPIO.setmode(GPIO.BCM)

#motor1
GPIO.setup(in1dc1,GPIO.OUT)
GPIO.setup(enadc1,GPIO.OUT)
GPIO.output(in1dc1,GPIO.HIGH)
p=GPIO.PWM(enadc1,1000)

#motor2
GPIO.setup(in1dc2,GPIO.OUT)
GPIO.setup(in2dc2,GPIO.OUT)
GPIO.setup(enadc2,GPIO.OUT)
p2=GPIO.PWM(enadc2,1000)

#motor3
GPIO.setup(in3dc3,GPIO.OUT)
GPIO.setup(enbdc3,GPIO.OUT)
GPIO.output(in3dc3,GPIO.HIGH)
p3=GPIO.PWM(enbdc3,1000)


def method_request_handler(method_request):
    global checkStock
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
    servoproduct = servo.Servo(pca.channels[servoNumber])
    x=0.40
    servoproduct.fraction = x
    while x < 0.70:
        x = x + 0.01
        servoproduct.fraction = x
        sleep(0.05)
    while x > 0.40:
        x = x - 0.01
        servoproduct.fraction = x
        sleep(0.05)

def directioncargo(direction):
    servos = 6
    servoloop = servo.Servo(pca.channels[servos])
    x=0.55
    servoloop.fraction = x
    if direction == "left":
        while x <= 0.85:
            x = x + 0.007
            servoloop.fraction = x
            sleep(0.05)
        sleep(1)
        while x > 0.55:
            x = x - 0.007
            servoloop.fraction = x
            sleep(0.05)
    elif direction == "right":
        while x >= 0.25:
            x = x - 0.007
            servoloop.fraction = x
            sleep(0.05)
        sleep(1)
        while x < 0.55:
            x = x + 0.007
            servoloop.fraction = x
            sleep(0.05)

def drivetruck(location, direction):
    if location == "forward":
        GPIO.output(in1dc2,GPIO.HIGH)
        GPIO.output(in2dc2,GPIO.LOW)
    elif location == "backward":
        GPIO.output(in1dc2,GPIO.LOW)
        GPIO.output(in2dc2,GPIO.HIGH)
    p2.start(40)
    sleep(1)
    p2.ChangeDutyCycle(0)
    sleep(1)
    directioncargo(direction)
    if location == "forward":
        GPIO.output(in1dc2,GPIO.LOW)
        GPIO.output(in2dc2,GPIO.HIGH)
    elif location == "backward":
        GPIO.output(in1dc2,GPIO.HIGH)
        GPIO.output(in2dc2,GPIO.LOW)
    p2.ChangeDutyCycle(40)
    sleep(1)
    p2.ChangeDutyCycle(0)


def StartProcess():

    print('')
    print('')
    print('Start processing.')


    p.start(28)

    for i in range(product1):
        storagethread(3)
        UpdateOrder("Product1")
        UpdateStock("Product1")
        sleep(1)
    for i in range(product2):
        storagethread(1)
        UpdateOrder("Product2")
        UpdateStock("Product2")
        sleep(1)
    for i in range(product3):
        storagethread(2)
        UpdateOrder("Product3")
        UpdateStock("Product3")
        sleep(1)
    for i in range(product4):
        storagethread(0)
        UpdateOrder("Product4")
        UpdateStock("Product4")
        sleep(1)

    print(store)
    sleep(3)
    p.ChangeDutyCycle(0)
    sleep(2)
    print('All products are processed.')
    if store == "conxion":
        drivetruck("forward", "left")
    elif store == "delhaize":
        drivetruck("forward", "right")
    elif store == "aldi":
        drivetruck("backward", "left")
    elif store == "colruyt":
        drivetruck("backward", "right")
    print('All products are delivered.')

def DeleteInProgress():
    global checkSQL
    if checkSQL == False
        sleep(1)
    checkSQL = False
    cursor.execute("delete from dbo.Progress where OrderNumber = '{}'".format(OrderNumber))
    cnxn.commit()
    checkSQL = True

def GetProgressRows():
    global checkSQL
    if checkSQL == False
        sleep(1)
    checkSQL = False
    cursor.execute("select COUNT(*) from dbo.Progress")
    row = cursor.fetchone() 
    while row: 
        global rowcount
        rowcount = row[0]
        row = cursor.fetchone()
    checkSQL = True

def UpdateStock(product):
    global checkSQL
    if checkSQL == False
        sleep(1)
    checkSQL = False
    cursor.execute("update dbo.Stock set {} = {} - 1".format(product, product))
    cnxn.commit()
    checkSQL = True

def UpdateStatus(message):
    global checkSQL
    if checkSQL == False
        sleep(1)
    checkSQL = False
    cursor.execute("update dbo.Orders set Status = '{}' where OrderNumber = '{}'".format(message, OrderNumber))
    cnxn.commit()
    checkSQL = True

def UpdateInProgress():
    global checkSQL
    if checkSQL == False
        sleep(1)
    checkSQL = False
    cursor.execute("update dbo.Progress set InProgress = 1 where OrderNumber = '{}'".format(OrderNumber))
    cnxn.commit()
    checkSQL = True

def UpdateOrder(product):
    global checkSQL
    if checkSQL == False
        sleep(1)
    checkSQL = False
    cursor.execute("update dbo.Progress set {} = {} - 1 where OrderNumber = '{}'".format(product, product , OrderNumber))
    cnxn.commit()
    checkSQL = True

def AddStock(product):
    global checkSQL
    if checkSQL == False
        sleep(1)
    checkSQL = False
    cursor.execute("update dbo.Stock set {} = {} + 1;".format(product, product))
    cnxn.commit()
    checkSQL = True

def GetStock():
    #print('stock nemen')
    global checkSQL
    if checkSQL == False
        sleep(3)
    checkSQL = False
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
    checkSQL = True


def GetOrder():
    global checkSQL
    if checkSQL == False
        sleep(3)
    checkSQL = False
    #print('order nemen')
    cursor.execute("select top 1 o.OrderNumber, o.Store, p.Product1, p.Product2, p.Product3, p.Product4, p.InProgress from dbo.Orders o inner join dbo.Progress p on o.OrderNumber = p.OrderNumber where (o.OrderNumber = p.OrderNumber) order by o.Id;") 
    row = cursor.fetchone()
    while row:
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
        product2 = row[3]
        product3 = row[4]
        product4 = row[5]
        InProgress = row[6]
        row = cursor.fetchone()
    checkSQL = True
    
def OrderMethod():
    checkStock = False
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
                        sleep(2)
                    else:
                        print('Not enough stock.')
                        sleep(5)
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
            checkStock = True
            print('Done.')
            print('')
            print('')
            break

def run():
    global check
    print("Connected.")
    check = 0
    while True:
        if check == 0:
            print('Script execution.')
            OrderMethod()
            check = 1
        else:
            False



def triggerTunnelServo():
    global camCheck
    global cap
    camCheck = False
    cap.release()
    x = 1
    tunnelServo.fraction = x
    while x > 0.8:
        x = x - 0.01
        tunnelServo.fraction = x
        sleep(0.05)
    while x < 1:
        x = x + 0.01
        tunnelServo.fraction = x
        sleep(0.05)
    tunnelServo.fraction = 1
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camCheck = True
def triggerSortingServo(color):

    if color == "red":
        AddStock("Product3")
        sortingServo.fraction = 0.58
    elif color == "white":
        AddStock("Product2")
        sortingServo.fraction = 0.42
    elif color == "yellow":
        AddStock("Product1")
        sortingServo.fraction = 0.75
    elif color == "green":
        AddStock("Product4")
        sortingServo.fraction = 0.24

def check_color(color):
    #IN BGR
    global colornow
    global colorcheck
    global i
    white_upper = (180, 180, 190)
    white_lower = (135, 130, 140)
    red_upper = (241, 96, 77)
    red_lower = (222, 45, 45)
    yellow_upper = (250, 222, 80)
    yellow_lower = (200, 155, 35)
    green_upper = (105, 190, 70)
    green_lower = (70, 140, 30)
    #print(color)
    if color[0] < red_upper[0] and color[0] > red_lower[0] and color[1] < red_upper[1] and color[1] > red_lower[1] and color[2] < red_upper[2] and color[2] > red_lower[2]:
        colornow = "red"
        #sleep(3)
    elif color[0] < yellow_upper[0] and color[0] > yellow_lower[0] and color[1] < yellow_upper[1] and color[1] > yellow_lower[1] and color[2] < yellow_upper[2] and color[2] > yellow_lower[2]:
        colornow = "yellow"
        #sleep(3)
    elif color[0] < green_upper[0] and color[0] > green_lower[0] and color[1] < green_upper[1] and color[1] > green_lower[1] and color[2] < green_upper[2] and color[2] > green_lower[2]:
        colornow = "green"
        #sleep(3)
    elif color[0] < white_upper[0] and color[0] > white_lower[0] and color[1] < white_upper[1] and color[1] > white_lower[1] and color[2] < white_upper[2] and color[2] > white_lower[2]:
        colornow = "white"
        #sleep(3)
    else:
        colornow = "empty"
    
    if colorcheck == colornow:
        i = i + 1
    elif colornow == "empty":
        colornow = colorcheck
    else:
        i = 0
    
    if i == 2:
        print(colornow)
        triggerSortingServo(colornow)
        triggerTunnelServo()
        i = 0

    colorcheck = colornow

def tunnelthread():
    global camCheck
    camCheck = True
    while True:
        if camCheck == True:
            _, frame = cap.read()
            cx = int(245)
            cy = int(150)
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
            #cv2.imshow("Frame", frame)
            cv2.waitKey(1)

#def methodhelper():
#    run = 0
#    device_client.connect()
#    print("Connected.")
#    #device_client.on_message_received = message_received_handler
#    device_client.on_method_request_received = method_request_handler
#    while run != 1:
#            try:
#                run = input()
#            except Exception as ex:
#                print(ex)
#            pass

def main():
    try:
        global checkSQL
        checkSQL = True
        runs = 1
        t1 = threading.Thread(target=tunnelthread)
        t2 = threading.Thread(target=run)
        #t3 = threading.Thread(target=methodhelper)
        t1.daemon = True
        t2.daemon = True
        #t3.daemon = True
        t1.start()
        t2.start()
        #t3.start()
        device_client.connect()
        device_client.on_method_request_received = method_request_handler
        while True:
            GetStock()
            if product1Stock < 10 or product2Stock < 10 or product3Stock < 10 or product4Stock < 10:
                print("go")
                p3.ChangeDutyCycle(17)
            else:
                print("stop")
                p3.ChangeDutyCycle(0)
            sleep(20)
    except KeyboardInterrupt:
        # clean up
        GPIO.output(in1dc1,GPIO.LOW)
        GPIO.output(in1dc2,GPIO.LOW)
        GPIO.output(in2dc2,GPIO.LOW)
        GPIO.output(in3dc3,GPIO.LOW)
        GPIO.output(enadc1,GPIO.LOW)
        GPIO.output(enadc2,GPIO.LOW)
        GPIO.output(enbdc3,GPIO.LOW)
        pca.deinit()
        device_client.disconnect()


if __name__ == '__main__':
    #--------------------------------
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    i = 0
    colorcheck = ""
    colornow = ""
    p3.start(0) #start conveyor
    main()