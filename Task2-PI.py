from __future__ import division
import cv2
import numpy as np
from math import cos, sin
from PIL import Image
import picamera
from time import sleep
import serial
import RPi.GPIO as GPIO

GPIO.setwarnings(False);



#pin 7 is for servo that rotates on X axis
b0 = 36
b1 = 38
b2 = 40

GPIO.setmode(GPIO.BOARD)
GPIO.setup(b0, GPIO.OUT)
GPIO.setup(b1, GPIO.OUT)
GPIO.setup(b2, GPIO.OUT)

green = (0, 255, 0)

def show(image):
    plt.figure(figsize=(10, 10))
    plt.imshow(image, interpolation='nearest')

def overlay_mask(mask, image):
    rgb_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    img = cv2.addWeighted(rgb_mask, 0.5, image, 0.5, 0)
    return img

def find_biggest_contour(image):
    image = image.copy()
    _, contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Isolate largest contour
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    mask = np.zeros(image.shape, np.uint8)
    return contours, mask

def circle_contour(image, contour):
    image_with_ellipse = image.copy()
    ellipse = cv2.fitEllipse(contour)
    cv2.ellipse(image_with_ellipse, ellipse, green, 2,cv2.LINE_AA)
    return image_with_ellipse

def find_ball(image):
    s=0
    done = False
    try:
        screenHeight, screenWidth,_ = image.shape
        screenMidX = screenWidth/2
        screenMidY = screenHeight/2
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_blur = cv2.GaussianBlur(image, (7, 7), 0)
        image_blur_hsv = cv2.cvtColor(image_blur, cv2.COLOR_RGB2HSV)
        min_green = np.array([60-25, 20, 20])
        max_green = np.array([60+25, 255, 255])
        #layer
        mask = cv2.inRange(image_blur_hsv, min_green, max_green)
        cnts, contours, hierarchy = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        
        largest_contour = sorted(contours, key=cv2.contourArea,reverse = True)
        
        if(len(largest_contour) > 0):
            cnts = largest_contour[0]
            cv2.drawContours(image, cnts, -1, (0, 255, 0), 2)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            centerballon = cv2.moments(cnts)
            cX = int(centerballon["m10"] / centerballon["m00"])
            cY = int(centerballon["m01"] / centerballon["m00"])
            cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
            cv2.putText(image, "X: "+str(cX), (cX - 20, cY - 40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(image, "Y: "+str(cY), (cX - 20, cY - 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            overlay = overlay_mask(mask, image)
            circled = circle_contour(overlay, cnts)
            print("Shape centerX/centerY: " + str(cX)+"/"+ str(cY))
            print("Area: " + str(cv2.contourArea(cnts)));
            print("Image centerX/centerY: " + str(screenMidX) +"/" + str(screenMidY))
            
            diff = screenMidX - cX
            if(float(str(cv2.contourArea(cnts)))>=160000):
                done = True
                print("DONE")
                s=4
                return [image,s, done]
            elif(float(str(cv2.contourArea(cnts)))<50):
                s=0;
                print("LESSS")
                
            elif(abs(diff) > 150):
                if(diff > 0):
                    print("Move left")
                    s=2
                if(diff < 0):
                    print("Move right")
                    s=3
            elif (abs(diff) <= 150):
                print("In Range")
                s=1
        if(len(largest_contour) == 0):
            print('No Green Color')
    except:
        print('Exception')    
        
    return [image,s, done]



    
    
cam = picamera.PiCamera()
c =0
v=[]
done=False;
if True:
#cam.start_preview(fullscreen=False,window=(0,0,640,480))
    cam.capture('/home/pi/Desktop/Pics/t'+str(c)+'.jpg')
    image = cv2.imread('/home/pi/Desktop/Pics/t'+str(c)+'.jpg')
    [result, action, done] = find_ball(image)
    print(action)

    
    while not done:
        c+=1;
        GPIO.output(b2, GPIO.LOW)

        if action ==2:
            GPIO.output(b1, GPIO.HIGH)
            GPIO.output(b0, GPIO.LOW)
            
        elif action == 3:
            GPIO.output(b1, GPIO.HIGH)
            GPIO.output(b0, GPIO.HIGH)
        elif action == 1:
            GPIO.output(b1, GPIO.LOW)
            GPIO.output(b0, GPIO.HIGH)        
        sleep(0.2);
        v.append(action);
        cam.capture('/home/pi/Desktop/Pics/t'+str(c)+'.jpg')
        image = cv2.imread('/home/pi/Desktop/Pics/t'+str(c)+'.jpg')
        [result, action, done] = find_ball(image)
        cv2.imwrite('/home/pi/Desktop/Pics/pics/out'+str(c)+'.jpg', result)
        print(done)

    dict ={1:0, 2:0, 3:0}
    for value in v:
        if value!=0:
            dict[value]=dict[value]+1;
        
    if dict[2] > dict[3]:
        dict[2] = dict[2] - dict[3]
        dict[3]=0
    elif dict[3]> dict[2]:
        dict[3] = dict[3]- dict[2]
        dict[2]=0
    else:
        dict[2]=0
        dict[1]=0
    print(dict)
    print("BYE")        
    for i in dict.keys():
        a = dict[i]
        if a!=0:
                if i==1 :
                    while a!=0:
                        a-=1
                        print("backwards")
                        GPIO.output(b2, GPIO.HIGH)
                        GPIO.output(b1, GPIO.LOW)
                        GPIO.output(b0, GPIO.LOW)
                        sleep(1);

                elif i==2 :
                    while a!=0:
                        a-=1
                        print("right")
                        GPIO.output(b2, GPIO.LOW)
                        GPIO.output(b1, GPIO.HIGH)
                        GPIO.output(b0, GPIO.HIGH)
                        sleep(1);

                elif i == 3:
                    while a!=0:
                        a-=1
                        print("left")
                        GPIO.output(b2, GPIO.LOW)
                        GPIO.output(b1, GPIO.HIGH)
                        GPIO.output(b0, GPIO.LOW)
                        sleep(1);
    
    print("stop");
        
    GPIO.output(b2, GPIO.LOW)
    GPIO.output(b1, GPIO.LOW)
    GPIO.output(b0, GPIO.LOW)
        
            
    
    

 

 

cam.stop_preview()
#cap.release()
#cv2.destroyAllWindows()    

