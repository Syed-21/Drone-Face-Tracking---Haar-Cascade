import cv2
import numpy as np
from djitellopy import tello
import time
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()
me.takeoff()
me.send_rc_control(0, 0, 20, 0)
time.sleep(1.2)

w,h = 420,600
pError = 0
fbRange=[6200,6800]
pid = [0.4,0.4,0]
def findface(img):
     faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
     imggray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
     faces=faceCascade.detectMultiScale(imggray,1.2,8)
     myFaceListC = []
     myFaceListA = []

     for (x,y,w,h) in faces:
         cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
         cx = x+w//2
         cy = y+h//2
         area = w*h
         cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)
         myFaceListC.append([cx,cy])
         myFaceListA.append(area)
     if len(myFaceListA) != 0:
         i = myFaceListA.index(max(myFaceListA))
         return img,[myFaceListC[i],myFaceListA[i]]
     else:
         return img,[[0,0],0]

def trackFace(info,w,pid,pError):
    area = info[1]
    x,y = info[0]
    fb= 0
    error = x - w //2
    speed = pid[0] * error + pid[1] * (error-pError)
    speed = int(np.clip(speed,-100,100))
    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb=-25
    elif area < fbRange[0] and area != 0:
        fb=25

    if x == 0 :
        speed = 0
        error = 0

    print(fb)
    me.send_rc_control(0,fb,0,speed)
    return error

# cap = cv2.VideoCapture(2)
while True :
    img = me.get_frame_read().frame
    img = cv2.resize(img,(h,w))
    img,info=findface(img)
    pError=trackFace( info, w, pid, pError)
    # print('ARea',info[1])
    cv2.imshow('image',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break