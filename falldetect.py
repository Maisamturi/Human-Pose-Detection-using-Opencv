# Author Zeyu Chen
# Falling Detection System

import json
import os
import math
import smtplib
import time
import cv2 as cv
import numpy as np
import subprocess
#import tkMessageBox
import tkinter
import tkinter.messagebox
from tkinter import *

from tkinter import filedialog
#from tkFileDialog import askopenfilename
#tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk

# Part1: Main
#
# Initializing

default_email = "alzahmeirpatientalert@gmail.com"
data_path = "sub_bg15"              # The default video path
valid_count = 0                    # The Frame Counter
old_valid_count = 0

# Initializing position information
average = 0
x_old = y_old = 0
head_x_old = head_y_old = 0
x_old_speed = x_speed = 0
y_old_speed = y_speed = 0
head_x_old_speed = head_x_speed = 0
head_y_old_speed = head_y_speed = 0

# Initializing Software Setting
target_email = default_email
target_video = data_path
old_frame = -30
ip_camera = ""

# Read the distance mapping file
distance_list = np.loadtxt('distance.txt')
distance = 0

# Part 2: Function
#
# Email
def send_alert():
    global target_email
    sender = 'alzahmeirpatientalert@gmail.com'
    receiver = 'itizazhussain565@gmail.com'

    message = """From: From Alzahemir Patient Monitor Activity <alzahmeirpatientalert@gmail.com>
    To: <itizazhussain565@gmail.com>
    Subject: Fall Alert

    Patient Fall on Ground. Please help.
    """

    try:
        session = smtplib.SMTP('smtp.gmail.com:587')
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(sender,'ali8161836')
        session.sendmail(sender,receiver,message)
        session.quit()
        print ("Successfully sent email")
    except smtplib.SMTPException:
        print ("Error: unable to send email")
        
def send_alert1():
    global target_email
    sender = 'alzahmeirpatientalert@gmail.com'
    receiver = 'itizazhussain565@gmail.com'

    message = """From: From Alzahemir Patient Monitor Activity <alzahmeirpatientalert@gmail.com>
    To: <itizazhussain565@gmail.com>
    Subject: sleep alert

    Patient is unable to Sleep and Continuously changing position. PLEASE HELP!.
    """

    try:
        session = smtplib.SMTP('smtp.gmail.com:587')
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(sender,'ali8161836')
        session.sendmail(sender,receiver,message)
        session.quit()
        print ("Successfully sent email")
    except smtplib.SMTPException:
        print ("Error: unable to send email")
        
def send_alert2():
    global target_email
    sender = 'alzahmeirpatientalert@gmail.com'
    receiver = 'itizazhussain565@gmail.com'

    message = """From: From Alzahemir Patient Monitor Activity <alzahmeirpatientalert@gmail.com>
    To: <itizazhussain565@gmail.com>
    Subject: hyperactivity alert

    Hyper Acticity seen in Patient behaviour. PLEASE HELP!
    """

    try:
        session = smtplib.SMTP('smtp.gmail.com:587')
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(sender,'ali8161836')
        session.sendmail(sender,receiver,message)
        session.quit()
        print ("Successfully sent email")
    except smtplib.SMTPException:
        print ("Error: unable to send email")
# Do analysis
index = 0
enable = 1
def do_analysis():
    global index
    global video_canvas_img, img
    global x_old, y_old, x_old_speed, y_old_speed, x_speed, y_speed
    global head_x_old, head_y_old, head_x_old_speed, head_x_speed, head_y_old_speed, head_y_speed
    global enable
    global old_frame

    file = target_video + "/Data/" + target_video + "_" + str(index).zfill(12) + "_keypoints.json"               
    try:
        fh = open(file)
    except IOError:
        index = 0
        tkinter.messagebox.showinfo("Alert", "\nNo files to be analyzed.\n\nPlease reset and try again.")
    else:
        with open(file) as f:  
            if f == None:
                return
            data = json.load(f)
            x = [0]*18
            y = [0]*18
            head_count = 0
            if data['people']:
                for i in range(0, 18):
                    x[i] = data['people'][0]['pose_keypoints'][3*i]
                    y[i] = data['people'][0]['pose_keypoints'][3*i + 1]

            # Take neck to represent the body 
            x_now = x[1]
            y_now = y[1]
            # Also take head into consideration, first count valid key pints of head, then compute their mean position
            if x[0] :
                head_count = head_count + 1
            for i in range(0, 4):
                if x[i + 14]:
                    head_count = head_count + 1
            # Calculate head position 
            head_x_now = 0
            head_y_now = 0
            if head_count :
                head_x_now = (x[0] + x[14] + x[15] + x[16] + x[17])/ head_count
                head_y_now = (y[0] + y[14] + y[15] + y[16] + y[17])/ head_count

            # Calculate speed
            x_old_speed = x_speed
            y_old_speed = y_speed
            head_x_old_speed = head_x_speed
            head_y_old_speed = head_y_speed
            x_speed = x_now - x_old
            y_speed = y_now - y_old
            head_x_speed = head_x_now - head_x_old  
            head_y_speed = head_y_now - head_y_old  
            # old_speed = speed
            # speed = math.sqrt((x_now - x_old)*(x_now - x_old) + (y_now - y_old)*(y_now - y_old))
            x_average = (x_speed + x_old_speed)/2
            y_average = (y_speed + y_old_speed)/2
            head_x_average = (head_x_speed + head_x_old_speed)/2
            head_y_average = (head_y_speed + head_y_old_speed)/2
            
            print ("Frame:" + str(index) + " x_speed: " + str(x_average))
            print ("Frame:" + str(index) + " y_speed: " + str(y_average))
            print ("Frame:" + str(index) + " headx_speed: " + str(head_x_average))
            print ("Frame:" + str(index) + " heady_speed: " + str(head_y_average))
            print (" ")

            # Update the position
            x_old = x_now
            y_old = y_now
            head_x_old = head_x_now
            head_y_old = head_y_now

            # Update distance
            distance = Distance(x, y)
            # Fall judge
            Fall (x_average, y_average, head_x_average, head_y_average, index, distance)
            

        img = PhotoImage(file = target_video + "/Image/" + target_video + "_" + str(index).zfill(12) + "_rendered.png")
        img = img.subsample(1, 1) 
        video_canvas.itemconfig(video_canvas_img, image = img)      
        index = index + 1
        if enable == 1:
            next_job = video_canvas.after(1, do_analysis)

# Fall Judge
def Fall(x_speed, y_speed, head_x_speed, head_y_speed, frame, distance):
    global valid_count # Robust
    global old_valid_count
    global old_frame
    
    # A fall is detected when both head and body speed meets the requirement
    if y_speed > 5.5 and head_y_speed > 5.5: 
        valid_count = valid_count + 1

    # To avoid wrong detection, only 4 continued frames that meets the requirement are regarded as fall
    if old_valid_count == valid_count:
        valid_count = 0
    old_valid_count = valid_count
    if valid_count > 4 and index - old_frame > 30: # We do not want the system to detect the same fall once more
        print ("Fall Detected at Frame" + str(index) + ", " + "The person falls at " + str(distance) + " inches.")
        time.sleep(5)
        old_frame = index
        send_alert()
        valid_count = 0

# Distance
def Distance(x, y):
    global distance_list
    global distance
    global index

    # Estimate the diameter of the head
    h1 = math.sqrt((x[16] - x[17])*(x[16] - x[17]) + (y[16] - y[17])*(y[16] - y[17]))
    h2 = math.sqrt((x[14] - x[16])*(x[14] - x[16]) + (y[14] - y[16])*(y[14] - y[16]))
    h3 = math.sqrt((x[15] - x[17])*(x[15] - x[17]) + (y[15] - y[17])*(y[15] - y[17]))
    h4 = math.sqrt((x[15] - x[16])*(x[15] - x[16]) + (y[15] - y[16])*(y[15] - y[16]))
    h5 = math.sqrt((x[14] - x[17])*(x[14] - x[17]) + (y[14] - y[17])*(y[14] - y[17]))

    # If the point is zero which means it is invalid
    if x[14] == 0:
        h2 = h5 = 0
    if x[15] == 0:
        h3 = h4 = 0
    if x[16] == 0:
        h1 = h2 = h4 = 0
    if x[17] == 0:
        h1 = h3 = h5 = 0
    hmax = max(h1, h2, h3, h4, h5)

    # Calculate the distance
    if index == 1 or abs(distance - distance_list[int(round(hmax))]) < 50:
        distance = distance_list[int(round(hmax))]
    return distance

# Part 3: UI
#
def Reset():
    global index
    global old_frame
    old_frame = -30
    index = 1
    enable = 1
    do_analysis()
# Email Set


def Start():
    global enable
    global old_frame
    old_frame = -30
    enable = 1
    do_analysis()

def Pause():
    global enable
    enable = 0
def One_Frame():
    global index
    global video_canvas_img, img
    global x_old, y_old, x_old_speed, y_old_speed, x_speed, y_speed
    global head_x_old, head_y_old, head_x_old_speed, head_x_speed, head_y_old_speed, head_y_speed
    global enable
    global old_frame
    global valid_count # Robust
    global old_valid_count
    global target_video
    target_video="sleep"

    file = target_video + "/Data/" + target_video + "_" + str(index).zfill(12) + "_keypoints.json"               
    try:
        fh = open(file)
    except IOError:
        index = 0
        tkinter.messagebox.showinfo("Alert", "\nNo files to be analyzed.\n\nPlease reset and try again.")
    else:
        with open(file) as f:  
            if f == None:
                return
            data = json.load(f)
            x = [0]*18
            y = [0]*18
            head_count = 0
            if data['people']:
                for i in range(0, 18):
                    x[i] = data['people'][0]['pose_keypoints_2d'][3*i]
                    y[i] = data['people'][0]['pose_keypoints_2d'][3*i + 1]

            # Take neck to represent the body 
            x_now = x[1]
            y_now = y[1]
            # Also take head into consideration, first count valid key pints of head, then compute their mean position
            if x[0] :
                head_count = head_count + 1
            for i in range(0, 4):
                if x[i + 14]:
                    head_count = head_count + 1
            # Calculate head position 
            head_x_now = 0
            head_y_now = 0
            if head_count :
                head_x_now = (x[0] + x[14] + x[15] + x[16] + x[17])/ head_count
                head_y_now = (y[0] + y[14] + y[15] + y[16] + y[17])/ head_count

            # Calculate speed
            x_old_speed = x_speed
            y_old_speed = y_speed
            head_x_old_speed = head_x_speed
            head_y_old_speed = head_y_speed
            x_speed = x_now - x_old
            y_speed = y_now - y_old
            head_x_speed = head_x_now - head_x_old  
            head_y_speed = head_y_now - head_y_old  
            # old_speed = speed
            # speed = math.sqrt((x_now - x_old)*(x_now - x_old) + (y_now - y_old)*(y_now - y_old))
            x_average = (x_speed + x_old_speed)/2
            y_average = (y_speed + y_old_speed)/2
            head_x_average = (head_x_speed + head_x_old_speed)/2
            head_y_average = (head_y_speed + head_y_old_speed)/2
            

            print ("Frame:" + str(index) + " x_speed: " + str(x_average))
            print ("Frame:" + str(index) + " y_speed: " + str(y_average))
            print ("Frame:" + str(index) + " headx_speed: " + str(head_x_average))
            print ("Frame:" + str(index) + " heady_speed: " + str(head_y_average))
            print (" ")
            if head_x_average == 0.0 and head_y_average == 0.0: 
                valid_count = valid_count + 1
                if valid_count == 30:
                    print ("Sleep issue alert")
                    time.sleep(3)
                    valid_count = 0
                    old_valid_count = old_valid_count + 1
                    if old_valid_count == 6:
                        send_alert1()
                        old_valid_count = 0
                

            # Update the position
            x_old = x_now
            y_old = y_now
            head_x_old = head_x_now
            head_y_old = head_y_now

            # Update distance
            distance = Distance(x, y)
            # Fall judge
            #Fall (x_average, y_average, head_x_average, head_y_average, index, distance)
            

        img = PhotoImage(file = target_video + "/Image/" + target_video + "_" + str(index).zfill(12) + "_rendered.png")
        img = img.subsample(1, 1) 
        video_canvas.itemconfig(video_canvas_img, image = img)      
        index = index + 1
        if enable == 1:
            next_job = video_canvas.after(1, One_Frame)

def Real_Time():
    s2_out = subprocess.check_output([sys.executable, "test.py"],shell=True).decode().strip()
    print (s2_out)
    if s2_out == "result angry":
        print('Hyper-Activity detected')
        send_alert2()
    #subprocess.run('python test.py')
    #global data_path
    #global ip_camera
    #global enable

    #if ip_camera == "":
        #tkMessageBox.showinfo("Warning", "\nPlease Set WebCam Address!")
        #return

    #data_path = "real_time"
    #s = "rm -rf real_time"
    #os.system(s)
    #s = "./build/examples/openpose/openpose.bin --no_display --write_images real_time/Image/ --write_keypoint_json real_time/Data --net_resolution 640x480--ip_camera " + ip_camera
    #os.system(s)
    # time.pause(10)
    #enable = 1
    #do_analysis()
# UI TOP
top = Tk()
top.geometry("800x550")
top.title("Alzahmeir Patient monitoring System")

# Title
title_label = Label(top, text = "Hyperactivity, fall and Sleep Deprivation Monitoring and Notification \n System for Psychologically Disturbed Patients using Image Processing ", font = "Helvetica 16 bold")
title_label.pack(pady = 10) 

# Button
Buttons = Frame(top) 
Buttons.pack(side = 'left')
## Analyze Button
button_do = Button(Buttons, text = 'Fall Detect', width = 10, command = Start)
button_do.pack(pady = 10)

## Pause
button_Pause = Button(Buttons, text = 'Pause', width = 10, command = Pause)
button_Pause.pack(pady = 10)

## One Frame
button_Continue = Button(Buttons, text = 'Sleep', width = 10, command = One_Frame)
button_Continue.pack(pady = 10)

## Real Time
button_Real_Time = Button(Buttons, text = 'Hyper Activity', width = 10, command = Real_Time)
button_Real_Time.pack(pady = 10)

# Video
Videos = Frame(top, width=500, height=500)
Videos.pack(side = 'right')
video_canvas = Canvas(Videos, width=700, height=400)
video_canvas.pack()
Frame0 = PhotoImage(file = "logo.png")
Frame0 = Frame0.subsample(1, 1) #640*480
video_canvas_img = video_canvas.create_image(300, 200, image=Frame0)


top.mainloop()

