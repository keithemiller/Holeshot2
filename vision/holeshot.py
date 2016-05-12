import cv2
import serial
import time
import trackObjects
import findblobs
import coneCalculations
import averaging

class jetsonRobot:
    
    def __init__(self):
        pass

    def connect(self):
        self.ser = serial.Serial(
            port = '/dev/ttyACM0',
            baudrate=115200,
            parity = serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        print "IS OPEN---"
        print self.ser.isOpen()
        
        #self.ser.write('s100!')
        # The robot should be connected now
        #self.ser.write('t50!')

        #self.ser.close()
    
    def waitForButton(self):

        line = []
        print "Waiting for button..."
        while True:
            for c in self.ser.read():
                # If any data is sent back, good to go? lol    
                return

        print "Found button!"

    def closeSerial(self):
        self.ser.close()

if __name__ == "__main__":
    j = jetsonRobot()   
    #j.connect()

    time.sleep(1)

    #j.waitForButton()

    turnPID = coneCalculations.jetsonPID(0.06, 0, 0.0)

    #j.ser.write("t38!")
    t = trackObjects.trackObjects()
    
    cap = cv2.VideoCapture(0)   

    ret, frame = cap.read()

    cv2.imwrite('testimage.jpg', frame)    

    bytesToRead = j.ser.inWaiting()


    tmpCount = 0

    while (cap.isOpened()):
 
        #j.ser.write("t38!")

        ret, frame = cap.read()

        labImage = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        objects, someimg = findblobs.findBlobs(labImage, True)          

        t.update(objects)

        targetPos, targetHeight = coneCalculations.getTargetPosition(t.getObjects())
   
        height, width = labImage.shape[:2]

        error = targetPos[0] - width/2
        #error, weightsum = averaging.getOrangeError(labImage)
        #print "WEIGHTSUM = " + str(weightsum)
        #turnPID.kP = -weightsum*0.00004 + 0.06
        turnPID.kP = targetHeight*0.0005 + 0.01

        if turnPID.kP < 0:
            turnPID.kp = 0

        turnFeedback = int(turnPID.update(error, 1))
        if (turnFeedback > 50): turnFeedback = 50
        if (turnFeedback < -50): turnFeedback = -50

        turnFeedback += 50  

        print "FEEDBACK = " + str(turnFeedback)

        j.ser.write("s" + str(turnFeedback) + "!")
        time.sleep(0.05);
        j.ser.write("t35!")
        j.ser.flush()
         
        cv2.line(someimg, (width/2, height), targetPos, (255, 0, 255), 2)

        for obj in t.getObjects():
            rect = obj.getRect()
            cv2.rectangle(someimg, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 255), 2)
            cv2.putText(someimg, str(obj.newid), (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255))
    
        cv2.imshow('testimage', someimg)    
       
        bytesToRead = j.ser.inWaiting()

        if bytesToRead > 0:
            j.ser.read(bytesToRead)
            if (tmpCount >= 2):
                break
            tmpCount+=1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()   
    j.closeSerial()
