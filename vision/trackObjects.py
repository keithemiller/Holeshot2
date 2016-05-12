import findblobs
import cv2

class trackableObject:

    # Rectangle is in the format x1, y1, x2, y2
    def __init__(self, rectangle, _id):
        self.rect = rectangle # Actual Rectangle
        self.newid = _id # ID of this object
    
    def getCenter(self):
        return ((self.rect[0] + self.rect[2])/2, (self.rect[1] + self.rect[3])/2) 

    # Returns C^2
    def getDistance(self, center):
        thiscenter = self.getCenter()

        return (thiscenter[0] - center[0])**2 + (thiscenter[1] - center[1])**2

    def getRect(self):
        return self.rect

    def applyNewObject(self, obj):
        self.rect = obj.getRect()

class trackObjects:

    def __init__(self):
        self.allset = False

    def getObjects(self):
        return self.objects

    def update(self, newlist):
            
        if self.allset is False:

            self.newid = 0
            self.allset = True
            self.objects = []
            
            for obj in newlist:
                self.objects.append(trackableObject(obj, self.newid))
                self.newid += 1
            return
 
        newobjects = []
        print "New List = " + str(newlist) 
        for obj in newlist:
            newobjects.append(trackableObject(obj, 0))
      
        for obj in self.objects:
            lowestDistance = 100000
            lowestDistanceIndex = -1            
            index = 0
            for newobj in newobjects:
                thisDist = newobj.getDistance(obj.getCenter())
                if thisDist < lowestDistance:
                    lowestDistance = thisDist 
                    lowestDistanceIndex = index
                
                index += 1 

            # Update connected objects from old frame to new frame
            if lowestDistance < 8000:
                closestObject = newobjects[lowestDistanceIndex]
                obj.applyNewObject(closestObject)
                newobjects.remove(closestObject)

            # Remove Untracked Objects
            else:
                self.objects.remove(obj) 

        for obj in newobjects:
            obj.newid = self.newid
            self.newid += 1
            self.objects.append(obj)

    def printObjects(self):
        for obj in self.objects:
            print "Object " + str(obj.newid) + " : " + str(obj.rect) 

if __name__ == "__main__":

    t = trackObjects()
       
    cap = cv2.VideoCapture("../testing/testvideo3.avi") 

    while (cap.isOpened()):
        
        ret, frame = cap.read()

        labImage = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        objects, someimg = findblobs.findBlobs(labImage, True)    
        
        t.update(objects)
        t.printObjects() 
      
        for obj in t.getObjects(): 

            rect = obj.getRect()
            cv2.rectangle(someimg, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 255), 2) 
            cv2.putText(someimg, str(obj.newid), (rect[0], rect[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255)) 
        cv2.imshow('testimage', someimg)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
 
    cap.release()
