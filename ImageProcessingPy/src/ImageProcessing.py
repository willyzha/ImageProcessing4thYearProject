import numpy as np
import argparse
import cv2
from _collections import deque
from collections import namedtuple
import WebcamModule
from math import sqrt

# initialize the current frame of the video, along with the list of
# ROI points along with whether or not this is input mode
roiPts = []
inputMode = False
DEBUG = False

def selectROI(event, x, y, flags, param):
    # if we are in ROI selection mode, the mouse was clicked,
    # and we do not already have four points, then update the
    # list of ROI points with the (x, y) location of the click
    # and draw the circle
    if inputMode and event == cv2.EVENT_LBUTTONDOWN and len(roiPts) < 4:
        roiPts.append((x, y))
        cv2.circle(param, (x, y), 4, (0, 255, 0), 2)
        cv2.imshow("frame", param)

def getHSVMask(frame, lowerb, upperb):
    if lowerb[0] < upperb[0]:
        return cv2.inRange(frame, lowerb, upperb)
    else:
        temp = upperb
        temp[0] = 255
        mask1 = cv2.inRange(frame, lowerb, temp)
        temp = lowerb
        temp[0] = 0
        mask2 = cv2.inRange(frame, temp, upperb)
        return cv2.bitwise_or(mask1, mask2)
    
def drawCrossHair(frame, x, y, size):
    cv2.line(frame, (x+size, y),(x-size,y),color=(0,0,255),thickness=1)
    cv2.line(frame, (x, y+size),(x,y-size),color=(0,0,255),thickness=1)
    
def compareHist(frame, window, modelHist):  
    #print window
    
    #roi = orig[tl[1]:br[1], tl[0]:br[0]]
    #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    roi = frame[window.y:window.y+window.h, window.x:window.x+window.w]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
   
    lowerb = np.array([39,40,90])
    upperb = np.array([100,255,255])
    mask  = getHSVMask(roi, lowerb, upperb)
    
    cv2.imwrite("mask.jpg", mask)
    cv2.imwrite("roi.jpg", roi)
    
    #print mask.shape
    #print roi.shape
    
    newHist = cv2.calcHist([roi], [0], mask, [16], [0, 180])
    diff = cv2.compareHist(newHist, modelHist, cv2.HISTCMP_BHATTACHARYYA)
    return diff

def drawOverlay(targetFrame,crossHair=None, boxPts=None, textToDraw=[], pointsToDraw=[]):
    
    if crossHair is not None:
        drawCrossHair(targetFrame, crossHair[0], crossHair[1], crossHair[2])
    
    if boxPts is not None:
        cv2.polylines(targetFrame, [boxPts], True, (0, 255, 0), 2)   
    
    for text in textToDraw:
        cv2.putText(targetFrame, text=text.text, org=text.origin, 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5, 
            color=text.color,thickness=1, lineType=cv2.LINE_AA)

    for point in pointsToDraw:
        cv2.circle(targetFrame,(point.x,point.y),2,point.color,thickness=3)


#INPUT  start ROI location (RotatedRect)
#       roiHistogram (MAT)
#OUTPUT center of new ROI
def camShiftTracker(aFrame, aRoiBox, aRoiHist):
    # initialize the termination criteria for cam shift, indicating
    # a maximum of ten iterations or movement by a least one pixel
    # along with the bounding box of the ROI
    termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
    
    # convert the current aFrame to the HSV color space
    # and perform mean shift
    hsv = cv2.cvtColor(aFrame, cv2.COLOR_BGR2HSV)
    
    # Mask to remove the low S and V values (white & black)
    lowerb = np.array([0,40,90])
    upperb = np.array([255,255,255])
    mask = getHSVMask(hsv, lowerb, upperb)
    kernel = np.ones((3,3),np.uint8)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel)
    
    
    backProj = cv2.calcBackProject([hsv], [0], aRoiHist, [0, 180], 1)
    backProj = cv2.morphologyEx(backProj,cv2.MORPH_OPEN, kernel)
    newBackProj = backProj#cv2.bitwise_and(backProj, mask)
    # apply cam shift to the back projection, convert the
    # points to a bounding box, and then draw them
    newBackProj = cv2.medianBlur(newBackProj, 5)
     
    (rotatedRect, aRoiBox) = cv2.CamShift(newBackProj, aRoiBox, termination)
    rotatedRectPts = np.int0(cv2.boxPoints(rotatedRect))
    
    center = np.uint16(np.around(rotatedRect[0]))
    
    x, y, width, height = cv2.boundingRect(rotatedRectPts)
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    
    rect = namedtuple('boundingRect', ['x', 'y', 'w', 'h'])
    boundingRect = rect(x, y, width, height)
    
    if DEBUG:
        roi = newBackProj[y:y+height, x:x+width]
        
        cv2.imshow("mask", mask)
        cv2.imshow("backProj", backProj)
        cv2.imshow("newBackProj", newBackProj) 
        cv2.imshow("roi",roi)   
    
    return (center, boundingRect, aRoiBox, rotatedRectPts)

def redetectionAlg(aFrame, aRoiHist, aLastArea, threshold):
    
    # Step1: Find HSV backproject of the frame
    hsv = cv2.cvtColor(aFrame, cv2.COLOR_BGR2HSV)
    mask = getHSVMask(aFrame, (0, 40, 90), (255,255,255))
    backProj = cv2.calcBackProject([hsv], [0], aRoiHist, [0, 180], 1)
    
    # Step2: Binarize Backprojection
    ret2, th2 = cv2.threshold(backProj, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    maskedThresh = cv2.bitwise_and(th2, mask)
    
    # Step3: Erode and Dilate
    kernel = np.ones((5,5),np.uint8)
    maskedThresh = cv2.morphologyEx(th2, cv2.MORPH_OPEN, kernel)
    cv2.imshow("th2", th2)
    # NOTE WZ: can try cv2.CHAIN_APPROX_NONE for no approximation
    im2, contours, hierarchy = cv2.findContours(maskedThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    tempFrame = aFrame.copy()
    

    
    # Step4: Find candidate regions with appropriate size of 30%
    largeContours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= (aLastArea * 0.3):
            largeContours.append(contour)

    cv2.drawContours(tempFrame, largeContours, -1, (0, 255,0), 3)
    cv2.imshow("tempFrame", tempFrame)

    matchedRect = None
    for contour in largeContours:
        x, y, width, height = cv2.boundingRect(contour)
        rect = namedtuple('boundingRect', ['x', 'y', 'w', 'h'])
        boundingRect = rect(x, y, width, height)
        
        diff = compareHist(aFrame, boundingRect, aRoiHist)
        print diff, threshold
        
        if diff < threshold:
            matchedRect = boundingRect

    if matchedRect is None:
        print "redetect failed"
    else:
        print "redetect successful"

    return matchedRect

def processImage(resolution, avgFilterN, *cameraIn):
    global roiPts, inputMode

    # if camera is not passed in then use default webcam
    camera = None
    if cameraIn:
        camera = cameraIn[0]
    else:
        camera = WebcamModule.Webcam(resolution)    

    # setup the mouse callback
    cv2.namedWindow("frame")

    roiBox = None
    modelHist = None
    
    avgFilterX = AveragingFilter(avgFilterN)
    avgFilterY = AveragingFilter(avgFilterN)
    
    trackingLost = False
    lastArea = 0

    #diffAvg = MovingAvgStd()
    
    #For matlab analysis
    #open("../../MatlabScripts/diff.txt", "w").close()

    # keep looping over the frames
    while True:
        # grab the current frame
        (grabbed, frame) = camera.getFrame()
        
        # check to see if we have reached the end of the
        # video
        if not grabbed:
            print "Could not read from camera exiting..."
            break

        outputFrame = frame.copy()
        
        # if the see if the ROI has been computed
        if roiBox is not None and modelHist is not None:
            if not trackingLost:
                (center, roiBoundingBox, roiBox, pts) = camShiftTracker(outputFrame, roiBox, modelHist)
                diff = compareHist(frame, roiBoundingBox, modelHist)
                
                lastArea = roiBoundingBox.h * roiBoundingBox.w
                
                if diff > 0.4:
                    print "TrackingFailed"
                    print "diff=" + str(diff)
                    
                    #roiBox
                    
                    trackingLost = True
                    #print "mean,std=" + str(diffAvg.getMeanStd())
    #                 roiBox = None
    #                 roiPts = []
                else:
                    #diffAvg.update(diff)
                    avgFilterX.add(center[0])
                    avgFilterY.add(center[1])
                    
                    xPos = avgFilterX.getAverage()
                    yPos = avgFilterY.getAverage()
                        
                    error = (resolution[0]/2-xPos, resolution[1]/2-yPos)
                    
                    text = namedtuple('text', ['text', 'origin', 'color'])
                    point = namedtuple('point', ['x', 'y', 'color'])
                                    
                    avgPointText = text("("+str(xPos)+","+str(yPos)+")", (xPos+10,yPos), (255,0,0))
                    errorText = text("err=("+str(error[0])+","+str(error[1])+")", (10,resolution[1]-10), (255,0,0))
                    diffText = text("diff=("+'{0:.5f}'.format(diff)+")", (150,resolution[1]-10), (255,0,0))
                    #stdText = text("mean,std=("+'{0:.5f}'.format(diffAvg.getMeanStd()[0]) + "," +'{0:.5f}'.format(diffAvg.getMeanStd()[1]) + ")", 
                    #                (275,resolution[1]-10), (255,0,0))
                    
                    avgCenterPoint = point(xPos, yPos, (255,0,0))
                    trueCenterPoint = point(center[0], center[1], (0,0,255))
                    
                    drawOverlay(outputFrame,
                                boxPts=pts,
                                textToDraw=[avgPointText, errorText, diffText],
                                pointsToDraw=[trueCenterPoint, avgCenterPoint])
            else: #Tracking is lost therefore begin running redetectionAlg
                redetectRoi = redetectionAlg(frame, modelHist, lastArea, 0.4)
                if redetectRoi is not None:
                    roiBox = redetectRoi
                    trackingLost = False
            
            
            # For matlab analysis
            # fo = open("../../MatlabScripts/diff.txt", 'a')
            # fo.write(str(diff)+'\n')
            
        # show the frame and record if the user presses a key
                
        drawOverlay(outputFrame, 
                    crossHair=(resolution[0]/2, resolution[1]/2, 10))
        cv2.imshow("frame", outputFrame)
        
        if DEBUG:
            cv2.imwrite("frame.jpg", outputFrame);
        
        key = cv2.waitKey(1) & 0xFF

        # handle if the 'i' key is pressed, then go into ROI
        # selection mode
        if key == ord("i") and len(roiPts) < 4:
            # indicate that we are in input mode and clone the
            # frame
            inputMode = True
            orig = frame.copy()

            # keep looping until 4 reference ROI points have
            # been selected; press any key to exit ROI selction
            # mode once 4 points have been selected
            while len(roiPts) < 4:
                cv2.setMouseCallback("frame", selectROI, frame)
                cv2.waitKey(0)

            # determine the top-left and bottom-right points
            roiPts = np.array(roiPts)
            s = roiPts.sum(axis = 1)
            tl = roiPts[np.argmin(s)]
            br = roiPts[np.argmax(s)]

            # grab the ROI for the bounding box and convert it
            # to the HSV color space
            roi = orig[tl[1]:br[1], tl[0]:br[0]]
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)

            # compute a HSV histogram for the ROI and store the
            # bounding box
            lowerb = np.array([39,40,90])
            upperb = np.array([100,255,255])
            mask  = getHSVMask(roi, lowerb, upperb)
            modelHist = cv2.calcHist([roi], [0], mask, [16], [0, 180])
            modelHist = cv2.normalize(modelHist, modelHist, 0, 255, cv2.NORM_MINMAX)
            
            if DEBUG:
                print modelHist
            
            roiBox = (tl[0], tl[1], br[0], br[1])
            cv2.setMouseCallback("frame", selectROI, None)
        # if the 'q' key is pressed, stop the loop
        elif key == ord("q"):
            print "Quitting"
            break

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()

class AveragingFilter:
    'Calculates rolling average'
    def __init__(self, n):
        self.n = n    
        self.queue = deque(np.full(10,-1,np.dtype(np.int32)), maxlen=n)
        self.sum = 0
        self.numEntries = 0
        
    def add(self, value):
        removedVal = self.queue.popleft()
        self.queue.append(value)
        
        if removedVal == -1:
            self.sum = self.sum + value
            self.numEntries = self.numEntries + 1
        else:
            self.sum = self.sum + value - removedVal
        
    def getAverage(self):
        if(self.numEntries > 0):
            return self.sum/self.numEntries
        else:
            return -1
        
class MovingAvgStd:
    # Keeps track of mean and standard deviation
    def __init__(self):
        self.count = 0
        self.mean = 0
        self.std = 0
        
    def update(self, data):
        origMean = self.mean
        
        self.count = self.count + 1
        self.mean = origMean + (data - origMean)/self.count
        if self.count > 2:
            self.std = sqrt((((self.count - 2) * self.std * self.std) + ((data - origMean)*(data-self.mean)))/(self.count - 1))

    def getMeanStd(self):
        return (self.mean, self.std)
    
    def inRange(self, data, nrStd):
        # For best results this should be checked before calling update
        if self.count > 100:
            return data <= self.mean + nrStd * self.std
        else:
            return True

def enableDebug():
    global DEBUG
    DEBUG = True
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform Camshift Tracking.\nUsage: \t"i" to select ROI\n\t"q" to exit' , formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('-d','--debug', dest='debug', action='store_const', const=True, default=False, help='enable debug mode. Displays multiple screens and saves .jpg images.')
    parser.add_argument('-filter', dest='avgFilterN', default=10, type=int, help='set length of averaging filter.')
    parser.add_argument('-resolution', dest='res', default=[640, 480], nargs=2, type=int, help='set resolution of camera video capture. usage: -resolution [X] [Y].')
    args = parser.parse_args()

    debug = args.debug
    avgFilterN = args.avgFilterN
    resolution = args.res
    
    if debug:
        enableDebug()
            
    processImage(resolution, avgFilterN)
    
