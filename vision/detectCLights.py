import cv2
import cv2.cv as cv
import numpy as np

class detectCLights:
    def __init__():
        pass


if __name__ == "__main__":
    cap = cv2.VideoCapture("../testing/changingLights.avi")
   
    ret, oldframe = cap.read()

    while (cap.isOpened()):
        ret, frame = cap.read()
        hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower = np.array([0, 0, 235])
        upper = np.array([180, 20, 255]) 

        mask = cv2.inRange(hsvImage, lower, upper)

        result = cv2.bitwise_and(frame, frame, mask = mask)

        subtraction = oldframe - result
        oldframe = result
    
        blurred = cv2.blur(subtraction, (25, 25))
       
        lower = np.array([100, 100, 100])
        upper = np.array([255, 255, 255])

        newmask = cv2.inRange(blurred, lower, upper)           

        # FInd Edges of things of interest
        edges = cv2.Canny(newmask, 30, 200)

        (cnts, _) = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

        if len(cnts) > 2:
            for c in cnts:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)

                print peri
                print approx

        cv2.imshow('testimage', edges)
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.imshow('testimage', frame)
