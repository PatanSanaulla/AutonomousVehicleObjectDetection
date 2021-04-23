import cv2
import numpy as np
import imutils
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import datetime
import RPi.GPIO as gpio
import os
import math
import serial
import emailIntegration as EMAIL

#Indentify serial communication
ser = serial.Serial('/dev/ttyUSB0', 9600)

forwardCount = 0
##### INit the pins
def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(31, gpio.OUT)
    gpio.setup(33, gpio.OUT)
    gpio.setup(35, gpio.OUT)
    gpio.setup(37, gpio.OUT)
    gpio.setup(36, gpio.OUT)
    gpio.output(36, False)
    gpio.setup(7, gpio.IN, pull_up_down = gpio.PUD_UP)
    gpio.setup(12, gpio.IN, pull_up_down = gpio.PUD_UP)
    
def gameover():
    gpio.output(31, False)
    gpio.output(33, False)
    gpio.output(35, False)
    gpio.output(37, False)
    gpio.cleanup()
    
def closeGripper():
    gpio.setmode(gpio.BOARD)
    gpio.setup(36, gpio.OUT)  #Gripper
    
    pwm = gpio.PWM(36, 50)
    pwm.start(5)
    
    rate = 0.15
    duty = float(3.5)
    while True:
        duty += rate
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.2)
        if duty >= 6.5:#6.25:
            break
    pwm.stop()
    #clear the output pins
    gpio.output(36, False)
    gpio.cleanup()

def openGripper():
    gpio.setmode(gpio.BOARD)
    gpio.setup(36, gpio.OUT)  #Gripper
    
    pwm = gpio.PWM(36, 50)
    pwm.start(5)
    
    rate = 0.15
    duty = float(6)
    while True:
        pwm.ChangeDutyCycle(duty)
        duty -= rate        
        time.sleep(0.2)
        if duty <= 3.5:
            break
    pwm.stop()
    #clear the output pins
    gpio.output(36, False)
    gpio.cleanup()
    
def forward(maxTicks):
    init()
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(37, 50) #Right side
    pwm2 = gpio.PWM(31, 50) #Left side
    val = 40
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)


    while True:      
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1
            
        if counterBR >= maxTicks:
            pwm1.stop()
            
        if counterFL >= maxTicks:
            pwm2.stop()
            
        if counterFL >= maxTicks and counterBR >= maxTicks:
            pwm1.stop()
            pwm2.stop()
            gameover()
            #Read serial stream
            #line = ser.readline() #print(line)
            #line = line.rstrip().lstrip()
            #line = str(line)
            #line = line.strip("'")
            #line = line.strip("b'")
            #print(line)
        
            #Return float
            #currAngle = float(line)
            #file.write(str(currAngle)+'\n')
            #file.write(str(currAngle)+','+str(maxTicks/98)+'\n')
            break
        
def reverse(maxTicks):
    init()
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(33, 50) #Right side
    pwm2 = gpio.PWM(35, 50) #Left side
    val = 40
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)


    while True:
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1
            
        if counterBR >= maxTicks:
            pwm2.stop()
            
        if counterFL >= maxTicks:
            pwm1.stop()
            
        if counterFL >= maxTicks and counterBR >= maxTicks:
            pwm1.stop()
            pwm2.stop()
            gameover()
            #Read serial stream
            #line = ser.readline() #print(line)
            #line = line.rstrip().lstrip()
            #line = str(line)
            #line = line.strip("'")
            #line = line.strip("b'")
            #print(line)
        
            #Return float
            #currAngle = float(line)
            #file.write(str(currAngle)+'\n')
            #file.write(str(currAngle)+','+str(maxTicks/98)+'\n')
            break

    
def pivotright(angle):
    init()
    offset = 1 #degrees
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(31, 50) #Right side
    pwm2 = gpio.PWM(35, 50) #Left side
    val = 35
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        line = ser.readline() #print(line)
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        goalAngle = (float(line) + angle)%360


    while True:
        #Read serial stream
        line = ser.readline() #print(line)
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        currAngle = float(line)
       
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1

        if currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
            pwm1.stop()
            pwm2.stop()
            gameover()
            break


def pivotleft(angle):
    init()
    offset = 1 #degrees
    counterBR = np.uint64(0)
    counterFL = np.uint64(0)

    buttonBR = int(0)
    buttonFL = int(0)

    # Initialize pwm signal to control motor
    pwm1 = gpio.PWM(33, 50) #Right side
    pwm2 = gpio.PWM(37, 50) #Left side
    val = 35
    pwm1.start(val)
    pwm2.start(val)
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        line = ser.readline() 
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        goalAngle = (float(line) - angle)%360

    while True:
        line = ser.readline() 
        line = line.rstrip().lstrip()
        line = str(line)
        line = line.strip("'")
        line = line.strip("b'")
        currAngle = float(line)
        
        if int(gpio.input(12)) != int(buttonBR):
            buttonBR = int(gpio.input(12))
            counterBR += 1
            
        if int(gpio.input(7)) != int(buttonFL):
            buttonFL = int(gpio.input(7))
            counterFL += 1

        if currAngle+offset >= goalAngle and currAngle-offset <= goalAngle:
            pwm1.stop()
            pwm2.stop()
            gameover()
            break
        

def detectOBI(image):
    global forwardCount
    height = (image.shape[0])
    width = (image.shape[1])
    
    #getting the HSV
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                     
    #threshold = cv2.inRange(hsvImage, (65, 60, 30), (85, 255, 255)) #Green
    threshold = cv2.inRange(hsvImage, (150, 70, 50), (180, 255, 255)) #Red
    
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #print(contours)
    
    centerX = int(640/2)
    centerY = int(480/2)
    
    #to print the center of the frame
    image = cv2.line(image, (centerX-20,centerY), (centerX+20,centerY), (0, 0, 0), 2)
    image = cv2.line(image, (centerX,centerY-20), (centerX,centerY+20), (0, 0, 0), 2)
    
    if len(contours) == 0:
        print('No block found')
    else:
        c = max(contours, key=cv2.contourArea)
        ((X,Y), radius) = cv2.minEnclosingCircle(c)
        image = cv2.circle(image, (int(X),int(Y)), int(radius), (0, 0, 255), 2)
        image = cv2.circle(image, (int(X),int(Y)), 2, (0, 0, 255), 2)
        
        cv2.putText(image, '('+str(X)+','+str(Y)+')', (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
        degrees = 0
        if(X > 315 and X < 325):
            if radius*2 > 400: #the object is close to the gripper
                closeGripper() #
                pic_time = 'pickedObject'#datetime.now().strftime('%Y%m%d%H%M%S')
                cv2.imwrite(pic_time+'.jpg', image)
                EMAIL.sendEmail(pic_time)
                reverse(forwardCount)
                forwardCount = 0
            else:
                forward(5)
                forwardCount += 5
             #   openGripper()
            return image #within the zone
        
        if(X < centerX):
            #rotate left
            degrees = (320 - X)*0.061
            pivotleft(degrees)
        else:
            #rotate right
            degrees = (640 - X)*0.061
            pivotright(degrees)
            
    return image
    
#cv2.drawContours(image, contours
# initialize the Raspberry Pi camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 25
rawCapture = PiRGBArray(camera, size=(640,480))

# allow the camera to warmup
time.sleep(0.1)

# define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('trackblockandretrive.avi', fourcc, 10, (640, 480))
# write frame to video file

# keep looping
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
    # grab the current frame
    start = datetime.datetime.now()
    
    image = frame.array
    image = cv2.rotate(image, cv2.ROTATE_180)
    
    processedImage = detectOBI(image)
    out.write(processedImage)
    
    # show the frame to our screen
    cv2.imshow("Frame", processedImage)
       
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # press the 'q' key to stop the video stream
    if key == ord("q"):
        gameover()
        break
    
#cv2.waitKey(0)
#cv2.destroyAllWindows()


