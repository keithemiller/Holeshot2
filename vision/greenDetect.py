import cv2
import numpy as np

if __name__ == "__main__":
    
    cap = cv2.VideoCapture(0)
    previousGreen = None

    kernel = np.ones((5, 5), np.uint8)   

    prevSum = 0

    ret, frame = cap.read()
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    hsvlower = np.array([179,57,0])
    hsvupper = np.array([255,255,255])
    
    firstFrame= cv2.inRange(hsvFrame, hsvlower, hsvupper)        
    prevdata = 0
    prevweightsum = 0
    while (cap.isOpened()):

        ret, frame = cap.read()
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    
        hsvgreen = cv2.inRange(hsvFrame, hsvlower, hsvupper)        
        
        output = hsvgreen - firstFrame
        
        data = cv2.countNonZero(output)
        velocity = (data - prevdata)
        
        print velocity


        if velocity > 500:
            print "GREEN!!!!!"

        prevdata = data
        cv2.imshow('ts',output) 
        cv2.imshow('ts2', firstFrame)
        cv2.imshow('live', hsvgreen)
        cv2.imshow('live2', frame)
        cv2.waitKey(1)
        continue

        green = cv2.inRange(frame, lower, upper)

        #green = cv2.dilate(green, kernel, iterations = 1)       
        green = hsvgreen
        green = cv2.blur(green, (5, 5)) 

        if (previousGreen is not None): 
            diff = hsvgreen - previousGreen
            previousGreen = hsvgreen
            data = cv2.countNonZero(diff)
            velocity = data - prevSum
            
            print velocity
            if (velocity > 5000):
                print "GREEN!"
            prevSum = data  

            cv2.imshow('testimage', diff)
            cv2.imshow('testimage2', green)

        if (previousGreen is None):
            previousGreen = hsvgreen
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
        
