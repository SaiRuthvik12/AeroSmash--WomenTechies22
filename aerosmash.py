from pickle import TRUE
from re import L
import cv2 as cv
from cv2 import sqrt
import math
import random
import sys
import subprocess
from playsound import playsound
import multiprocessing
import mediapipe as mp

from flask import Flask,render_template, Response
from flask import Flask, request

app = Flask(__name__)


# -------POSE DETECTION CLASS FUNCTIONS----------


class poseDetector():

    def __init__(self, mode=False, upBody=False, smooth=True, detectionCon = 0.5, trackCon =0.5):
        
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

    
    def findPose(self, img, draw = True):

        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        
        if self.results.pose_landmarks:
            if draw:
                 self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        
        return img

    def findPosition(self,img,draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h,w,c=img.shape
                #print(id,lm)
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id,cx,cy])
                if draw:
                    cv.circle(img, (cx,cy),5,(0,0,255),cv.FILLED)

        return lmList





# ----------MAIN RUNNER CODE------------




def generate_frames():
    wCam,hCam = 1920,1080
    cap = cv.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    count=0
    count2=1
    flag=0
    score=0
    check=0
    mode=60
    life=6
    counter=3
    detector = poseDetector()

    # -------DISTANCE CALCULATION FUNCTION--------

    def dist(x1,y1,x2,y2):
        distance = sqrt(((y2-y1)**2) + ((x2-x1)**2))
        #print(distance)
        return distance[0][0]

    
    # ----------OPENCV WEBCAM-------------

    while True:

        success, img = cap.read()
        img = cv.flip(img,1)
        img = cv.resize(img, (1280,720))
        img = detector.findPose(img)
        lmList = detector.findPosition(img,False)

        # ---------CHECK FOR START--------

        if(check==0):
            counter=3
            cv.putText(img,"START",(550,150),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),10)
            if len(lmList)!=0 :

                xlh = lmList[20][1];
                ylh = lmList[20][2];

                xrh = lmList[19][1];
                yrh = lmList[19][2];

                if(dist(xlh,ylh,570,150)<=100 or dist(xrh,yrh,570,150)<=100):
                    check=1
        
        
        # ---------CHECK FOR DIFFICULTY-------

        elif(check==1):
            cv.putText(img,"EASY",(50,50),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),10) 
            cv.putText(img,"MEDIUM",(550,50),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),10) 
            cv.putText(img,"HARD",(1100,50),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),10)

            if len(lmList)!=0 :

                xlh = lmList[20][1];
                ylh = lmList[20][2];

                xrh = lmList[19][1];
                yrh = lmList[19][2];

                if(dist(xlh,ylh,50,50)<=100 or dist(xrh,yrh,50,50)<=100):
                    check=2
                    mode=60

                if(dist(xlh,ylh,550,50)<=100 or dist(xrh,yrh,570,50)<=100):
                    check=2
                    mode=30

                if(dist(xlh,ylh,1100,50)<=100 or dist(xrh,yrh,1100,50)<=100):
                    check=2
                    mode=15



        # ----------CHECK FOR TIMER----------


        elif check==2 or check==3 or check==4:
            cv.putText(img,str(counter),(580,380),cv.FONT_HERSHEY_PLAIN,8,(255,0,255),22)
            if count2%30==0:
                counter-=1
                check+=1
            count2+=1
        

        # ----------CHECK FOR PLAYING THE GAME----------


        elif check==5 and life>0:
            if count%mode==0:
                xc = random.randint(40,1100)
                yc = random.randint(40,680)
                if(flag==0):
                    life=life-1
                
                flag=0
                

                

            count=count+1
            

            if flag==0:
                cv.circle(img, (xc,yc),30,(0,0,255),cv.FILLED)

            if flag==1:
                cv.circle(img, (xc,yc),30,(0,255,0),cv.FILLED)


            if len(lmList)!=0 :

                xlh = lmList[20][1];
                ylh = lmList[20][2];

                

                xrh = lmList[19][1];
                yrh = lmList[19][2];

                

                if(dist(xc,yc,xlh,ylh)<=100 or dist(xc,yc,xrh,yrh)<=100) and flag==0:
                    score=score+100
                    flag=1
                
                
            #print(score)
            scorefinal = "SCORE = " + str(score)
            lifefinal = "LIVES = " +str(life)
            cv.putText(img,scorefinal,(50,50),cv.FONT_HERSHEY_PLAIN,4,(255,0,255),10) 
            cv.putText(img,lifefinal,(800,50),cv.FONT_HERSHEY_PLAIN,4,(255,0,255),10) 



        # --------CHECK FOR DEATH----------



        else:
            cv.putText(img,"YOU DIED",(350,280),cv.FONT_HERSHEY_PLAIN,8,(255,0,255),22)
            cv.putText(img,scorefinal,(200,390),cv.FONT_HERSHEY_PLAIN,8,(255,0,255),22)
            cv.putText(img,"RESTART",(50,50),cv.FONT_HERSHEY_PLAIN,3,(255,0,255),10)

            xlh = lmList[20][1];
            ylh = lmList[20][2];

            xrh = lmList[19][1];
            yrh = lmList[19][2];

            if(dist(xlh,ylh,50,50)<=100 or dist(xrh,yrh,50,50)<=100):
                    count=0
                    count2=1
                    flag=0
                    score=0
                    check=0
                    mode=60
                    life=6
                    counter=3
        
        ret,buffer = cv.imencode('.jpg',img)
        img=buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-type: image/jpeg\r\n\r\n'+img+b'\r\n')
        #cv.imshow("Image",img)
        #cv.waitKey(1)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace;boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)