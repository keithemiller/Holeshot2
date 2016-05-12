#!/usr/bin/python

import cv2
import numpy as np

# Takes in an LAB image and returns boxes showing where relevant objects are  
# If objects are the correct shade of orange (in LAB colorspace), big enough, 
#  low enough in the image, it would be considerd a relevant objects.
def findBlobs(labImage, DEBUG):
   
    orangeLow = np.array([0, 145, 140])
    orangeHigh = np.array([255, 200, 210])

    mask = cv2.inRange(labImage, orangeLow, orangeHigh)
    output = cv2.bitwise_and(labImage, labImage, mask = mask)

    # Blur by alot so that alot of noise is cut out
    # blurredOutput = cv2.blur(output, (25, 25))
    kernel = np.ones((5, 5), np.uint8) 
    dilation = cv2.dilate(output, kernel, iterations=4) 
    blurredOutput = cv2.blur(dilation, (5, 5))

    # Create binary image
    ret, thresh1 = cv2.threshold(blurredOutput, 1, 255, cv2.THRESH_BINARY)

    # Find edges
    edged = cv2.Canny(thresh1, 30, 200)   

    # Find Contours 
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]    
    
    objs = []
    
    # Find Bounding Boxes of contours 
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
       
        # If the object is too small, don't bother including it
        if peri < 80:
            continue
         
        high = np.array([0,0])
        low = np.array([10000, 10000])

        # Find boundingbox
        for obj in approx:
            if obj[0][0] > high[0]:
                high[0] = obj[0][0]
            if obj[0][1] > high[1]:
                high[1] = obj[0][1]
            if obj[0][0] < low[0]:
                low[0] = obj[0][0]
            if obj[0][1] < low[1]:
                low[1] = obj[0][1] 
    
        # Add this object to the list of known objects    
        objs.append([0, low[0], low[1], high[0], high[1]])    
        
        cv2.drawContours(labImage, [c], -1, (0, 255, 0), 3)
  
    x1 = 1
    x2 = 3
    y1 = 2
    y2 = 4 

    height, width = labImage.shape[:2]
    
    CUTOFF_HEIGHT = 300 # Anything above this height (0 to 300) should not be considered a potentional object

    cv2.rectangle(labImage, (0, CUTOFF_HEIGHT), (width, CUTOFF_HEIGHT), (255, 255, 0), 1)
    cv2.rectangle(labImage, (width/2, 0), (width/2, height), (255, 255, 0), 1)
    # Find core objects in picture.  If multiple rectangles overlap, combine them.
    for obj in objs:
        if obj[0] != 0: continue
 
        for checkObj in objs:

            if obj is checkObj: continue
            if checkObj[0] != 0: continue # Already found

            # Check if intersecting, if not, check the next one
            if obj[y2] < checkObj[y1]: continue
            if checkObj[y2] < obj[y1]: continue
            if obj[x2] < checkObj[x1]: continue
            if checkObj[x2] < obj[x1]: continue
           
            obj[x1] = min(obj[x1], checkObj[x1])
            obj[x2] = max(obj[x2], checkObj[x2])
            obj[y1] = min(obj[y1], checkObj[y1])
            obj[y2] = max(obj[y2], checkObj[y2])
 
            checkObj[0] = 1 

    coreobjs = []

    # Go through all the core objects. Core objects have their 0 index set to 1
    for obj in objs:
        if obj[0] != 0: continue
        if obj[y2] < CUTOFF_HEIGHT: continue           

        coreobjs.append([obj[1], obj[2], obj[3], obj[4]])

        cv2.rectangle(labImage, (obj[x1], obj[y1]), (obj[x2], obj[y2]), (255,0,0), 1)

    # Return Bounding Boxes of core objects 
    return coreobjs, labImage
    

# Debugging 
if __name__ == "__main__":
    
    #cap = cv2.VideoCapture("../testing/testvideo3.avi")

    #while (cap.isOpened()):
    frame = cv2.imread('../testing/testimage2.jpg') #cap.read()
    
    labImage = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    x, someimg = findBlobs(labImage, True)
    cv2.imshow('testimage', someimg)

    cv2.waitKey(0)

    #cap.release() 
