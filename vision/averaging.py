import cv2
import numpy as np

def getOrangeError(labImage):
    orangeLow = np.array([0, 145, 140])
    orangeHigh = np.array([255, 200, 210])

    mask = cv2.inRange(labImage, orangeLow, orangeHigh)

    height, width = mask.shape[:2]

    mask = mask[300:height, 0:width]

    height, width = mask.shape[:2]
    
    total = 0
    weightsum = 0
    for i in range(0, width, 1):
        weight = cv2.countNonZero(mask[:,i])
        weightsum += weight
        total += (i - width/2)*weight

    if weightsum == 0:
        return 0, 0

    return float(total) / float(weightsum), weightsum

if __name__ == "__main__":
    frame = cv2.imread('../testing/testimage.jpg')

    labImage = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    for i in range(0, 25):
        print getOrangeError(labImage) 

