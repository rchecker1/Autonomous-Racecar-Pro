#!/usr/bin/env python
# encoding: utf-8
import cv2 as cv
import time

capture = cv.VideoCapture("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=0 ! video/x-raw, width=1280, height=720, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink", cv.CAP_GSTREAMER)

print ("capture get FPS : ",capture.get(cv.CAP_PROP_FPS))
while capture.isOpened():
    start = time.time()
    ret, frame = capture.read()
    if cv.waitKey(1) & 0xFF == ord('q'): break
    end = time.time()
    fps = 1 / (end - start)
    text="FPS : "+str(int(fps))
    cv.putText(frame, text, (20, 30), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 1)
    cv.imshow('frame', frame)
capture.release()
cv.destroyAllWindows()#!/usr/bin/env python
# encoding: utf-8
import cv2 as cv
import time

capture = cv.VideoCapture("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=0 ! video/x-raw, width=1280, height=720, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink", cv.CAP_GSTREAMER)

print ("capture get FPS : ",capture.get(cv.CAP_PROP_FPS))
while capture.isOpened():
    start = time.time()
    ret, frame = capture.read()
    if cv.waitKey(1) & 0xFF == ord('q'): break
    end = time.time()
    fps = 1 / (end - start)
    text="FPS : "+str(int(fps))
    cv.putText(frame, text, (20, 30), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 1)
    cv.imshow('frame', frame)
capture.release()
cv.destroyAllWindows()
