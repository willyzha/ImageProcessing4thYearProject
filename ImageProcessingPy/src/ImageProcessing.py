import numpy as np
import argparse
import cv2
from _collections import deque
from collections import namedtuple
from WebcamModule import Webcam
import time
from math import sqrt
from HistogramPlotter import plotHsvHist

# initialize the current frame of the video, along with the list of
# ROI points along with whether or not this is input mode
inputMode = False
DEBUG = False
TIME_ANALYSIS = False

# SELECT OPTIMIZED VALUES WITH MaskConfigurator or PiMaskConfigurator
LOWER_MASK_BOUND = np.array([0,40,90])
UPPER_MASK_BOUND = np.array([255,255,255])

# ENABLE/DISABLE TRACKING HALTING AND REDETECTION
RETECTION_ENABLED = False

text = namedtuple('text', ['text', 'origin', 'color'])
point = namedtuple('point', ['name', 'x', 'y', 'color', 'text'])
number = namedtuple('number', ['name', 'val', 'origin', 'color'])

def buttonPress(event):
    print event

class AveragingFilter:
    """ Calculates rolling average
    """
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
        
# Currently unused originally made for adaptive thresholding
class RunningAvgStd:
    """ Running average and standard deviation
    """ 
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

def printTime(text):
    if TIME_ANALYSIS:
            print (text + str(time.time()))

def getHSVMask(frame, lowerb, upperb):
    """ Finds the HSV mask for the input frame given a lower bound and upper bound
    """
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
    
def compareHist(frame, roiWindow, refHist):  
    """ Compares the histogram of the roiWindow in frame with refHist
    """
    # Get the submatrix for the region of interest and convert to HSV
    roi = frame[roiWindow[1]:roiWindow[1]+roiWindow[3], roiWindow[0]:roiWindow[0]+roiWindow[2]]
    #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
   
    # Use the same mask from the original histogram generation
    mask  = getHSVMask(roi, LOWER_MASK_BOUND, UPPER_MASK_BOUND)
    
    if DEBUG: # Write some the mask and ROI as .jpg files for debugging
        cv2.imwrite("mask.jpg", mask)
        cv2.imwrite("roi.jpg", roi)
    
    # Calculate the histogram for the region of interest
    newHist = cv2.calcHist([roi], [0], mask, [16], [0, 180])
    
    # Compare the new histogram with original for a diff of 0-1 
    # 1: no match/overlap
    # 0: perfect match
    diff = cv2.compareHist(newHist, refHist, cv2.HISTCMP_BHATTACHARYYA)
    return diff

def drawCrossHair(frame, x, y, size):
    """ Draw a cross hair
    """
    cv2.line(frame, (x+size, y),(x-size,y),color=(0,255,255),thickness=1)
    cv2.line(frame, (x, y+size),(x,y-size),color=(0,255,255),thickness=1)

def camShiftTracker(aFrame, aRoiBox, aRoiHist):
    """ Main CamShift tracking function
        Performs conversion and processing to find the next region of interest
        Inputs:
            aFrame=Updated frame from camera
            aRoiBox=Box around the previous region of interest
            aRoiHist=The pre-calculated Hue histogram for the object of interest
        Outputs: (center, boundingRect, newRoiBox, rotatedRectPts)
            center: coordinates for the updated center of the object
            boundingRect: bounding rectangle for the updated object location
            newRoiBox: updated RoiBox
            rotatedRectPts: corner coordinates for the rotated rectangle bounding object
    """
    # initialize the termination criteria for cam shift, indicating
    # a maximum of ten iterations or movement by a least one pixel
    # along with the bounding box of the ROI
    termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
    
    # convert the current aFrame to the HSV color space
    # and perform mean shift
    #hsv = cv2.cvtColor(aFrame, cv2.COLOR_BGR2HSV)
    hsv = aFrame
    
    # Mask to remove the low S and V values (white & black)
    #mask = getHSVMask(hsv, LOWER_MASK_BOUND, UPPER_MASK_BOUND)
    kernel = np.ones((3,3),np.uint8)
    #mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel)
    
    
    backProj = cv2.calcBackProject([hsv], [0], aRoiHist, [0, 180], 1)
    backProj = cv2.morphologyEx(backProj,cv2.MORPH_OPEN, kernel)
    newBackProj = backProj#cv2.bitwise_and(backProj, mask)
    # apply cam shift to the back projection, convert the
    # points to a bounding box, and then draw them
    newBackProj = cv2.medianBlur(newBackProj, 5)
     
    (rotatedRect, newRoiBox) = cv2.CamShift(newBackProj, aRoiBox, termination)
    rotatedRectPts = np.int0(cv2.boxPoints(rotatedRect))
    
    center = np.uint16(np.around(rotatedRect[0]))
    
    x, y, width, height = cv2.boundingRect(rotatedRectPts)
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    
    boundingRect = (x, y, width, height)
    
    if DEBUG:
        roi = newBackProj[y:y+height, x:x+width]
        
        #cv2.imshow("mask", mask)
        cv2.imshow("backProj", backProj)
        cv2.imshow("newBackProj", newBackProj) 
        cv2.imshow("roi",roi)   
    
    return (center, boundingRect, newRoiBox, rotatedRectPts)

def calculateFrameRate(deltaT):
    if deltaT == 0:
        return -1
    return int(round(1/deltaT))

def redetectionAlg(aFrame, aRoiHist, aLastArea, aDiffThresh):
    """ Algorithm for redetecting the object after it is lost
        Inputs:
            aFrame: Frame in which the object is to be searched for
            aRoiHist: The pre-calculated Hue histogram for the object of interest
            aLastArea: The area of ROI of the object when last seen
            aDiffThresh: Min difference threshold to determine the object is found
        Outputs: 
            matchedRect: Most probable rectangle around object. None if no matches were found
    """
    # Step1: Find HSV back projection of the frame
    #hsv = cv2.cvtColor(aFrame, cv2.COLOR_BGR2HSV)
    hsv = aFrame
    backProj = cv2.calcBackProject([hsv], [0], aRoiHist, [0, 180], 1)
    
    # Step2: Binarize Back Projection
    _, threshold = cv2.threshold(backProj, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
       
    # Step3: Erode and Dilate
    kernel = np.ones((5,5),np.uint8)
    maskedThresh = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

    # NOTE WZ: can try cv2.CHAIN_APPROX_NONE for no approximation
    _, contours, _ = cv2.findContours(maskedThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Step4: Find candidate regions with appropriate size of 30%
    candidateContours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= (aLastArea * 0.3):
            candidateContours.append(contour)

    if DEBUG:
        contourFrame = aFrame.copy()
        cv2.drawContours(contourFrame, candidateContours, -1, (0, 255,0), 3)
        cv2.imshow("DEBUG: Contours with 30% area", contourFrame)

    # Step5: Look through candidate contours and select the one with lowest diff that is below the diff threshold
    matchedRect = None
    minDiff = 1 # max diff is 1
    for contour in candidateContours:
        boundingRect = cv2.boundingRect(contour)       
        diff = compareHist(aFrame, boundingRect, aRoiHist)

        if diff < aDiffThresh and diff < minDiff:
            minDiff = diff
            matchedRect = boundingRect

    return matchedRect

class ImageProcessor:
    def __init__(self, cameraModule, res, avgFilterN):
        self.capturing = False
        self.camera = cameraModule
        self.resolution = res
        self.avgFilterN = avgFilterN
        self.roiPts = []
        self.outputMode = "BGR"
        self.showHistogram = False
        self.modelHist = None
        self.showFps = False
        
    def endImageProcessing(self):
        self.capturing = False
        self.roiPts = []
        if not DEBUG:
            cv2.destroyWindow("ModelHistogram")
        
    def quitImageProcessing(self):
        self.capturing = False
        self.camera.release()
        
    def setOutputMode(self, val):
        print val
        if val == "BGR":
            self.outputMode = "BGR"
        elif val == "HSVpure":
            self.outputMode = "HSVpure"         
        elif val == "HSVraw":
            self.outputMode = "HSVraw" 
        elif val == "None":
            self.outputMode = "None" 
        else:
            raise Exception("Not a valid output configuration!!")

    def setDebugMode(self, d):
        """ Enables debugging for the tracker
        """
        global DEBUG
        DEBUG = d

    def setShowHistogram(self, h):
        self.showHistogram = h
        if h:
            if self.modelHist is not None:
                cv2.imshow('ModelHistogram', plotHsvHist(self.modelHist))
        else:
            cv2.destroyWindow('ModelHistogram')

    def setShowFps(self, showFps):
        self.showFps = showFps

    def getDebug(self):
        return DEBUG

    def selectROI(self, event, x, y, flags, param):
        """ Mouse call back function for selection initial ROI containing the target object
        """
        # if we are in ROI selection mode, the mouse was clicked,
        # and we do not already have four points, then update the
        # list of ROI points with the (x, y) location of the click
        # and draw the circle
        if inputMode and event == cv2.EVENT_LBUTTONDOWN and len(self.roiPts) < 4:
            self.roiPts.append((x, y))
            cv2.circle(param, (x, y), 4, (60,255,255), 2)
            cv2.imshow("frame", cv2.cvtColor(param,cv2.COLOR_HSV2BGR))

    def displayOutput(self, aFrame):
        if self.outputMode is "BGR":
            cv2.imshow("frame", cv2.cvtColor(aFrame, cv2.COLOR_HSV2BGR))
        elif self.outputMode is "HSVpure":
            aFrame[:,:,2] = 255
            aFrame[:,:,1] = 255
            cv2.imshow("frame", cv2.cvtColor(aFrame, cv2.COLOR_HSV2BGR))
        elif self.outputMode is "HSVraw":
            cv2.imshow("frame", aFrame)

    def drawOverlay(self, targetFrame,crossHair=None, boxPts=None, textToDraw=[], pointsToDraw=[], numToDraw=None):
        """ Draws crossHair, boxes, text and points on the targetFrame
            WARNING: DO NOT DRAW ON PROCESSING FRAME!!!
        """
        if self.outputMode is "None" or DEBUG:
            outputText = ""
            for point in pointsToDraw:
                outputText = outputText + point.name+ "="  + point.text + " "
            
            for text in textToDraw:
                outputText = outputText + text.text + " "
                
            if numToDraw is not None:
                outputText = outputText + numToDraw.name + "=(" + str(numToDraw.val) + ")"
            
            print outputText

        if self.outputMode is not "None" or DEBUG:
            if crossHair is not None:
                drawCrossHair(targetFrame, crossHair[0], crossHair[1], crossHair[2])
            
            if boxPts is not None:
                cv2.polylines(targetFrame, [boxPts], True, (60, 255, 255), 2)   
            
            for text in textToDraw:
                cv2.putText(targetFrame, text=text.text, org=text.origin, 
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5, 
                    color=text.color,thickness=1, lineType=cv2.LINE_AA)
                
            if numToDraw is not None:
                cv2.putText(targetFrame, text=str(numToDraw.val), org=numToDraw.origin,
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5, 
                    color=numToDraw.color,thickness=1, lineType=cv2.LINE_AA)
        
            for point in pointsToDraw:
                cv2.putText(targetFrame, text=point.text, org=(point.x,point.y),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5, 
                    color=point.color,thickness=1, lineType=cv2.LINE_AA)
                cv2.circle(targetFrame,(point.x,point.y),2,point.color,thickness=3)

    def processImage(self):
        """ Main Loop Function for Tracking
        """
        global inputMode
        
        self.capturing = True
        
        printTime("Start processImage: ")
    
        # setup the mouse callback
        cv2.namedWindow("frame")
    
        roiBox = None
        
        avgFilterX = AveragingFilter(self.avgFilterN)
        avgFilterY = AveragingFilter(self.avgFilterN)
        
        trackingLost = False
        lastArea = 0

        #diffAvg = RunningAvgStd()
        startTime = time.time()        
        #For matlab analysis
        #open("../../MatlabScripts/diff.txt", "w").close()
        
        # keep looping over the frames
        while self.capturing:
            
            printTime(" Start getFrame(): ")
            
            # grab the current frame
            (grabbed, frame) = self.camera.getFrame()
            printTime(" End getFrame(): ")
            # check to see if we have reached the end of the
            # video
            if not grabbed:
                print "Could not read from camera exiting..."
                break
    
            #outputFrame = frame.copy()
            
            # if the see if the ROI has been computed
            if roiBox is not None and self.modelHist is not None:
                printTime(" Start tracking: ")
                if not trackingLost:
                    printTime("  Start camShift: ")
                    (center, roiBoundingBox, roiBox, pts) = camShiftTracker(frame, roiBox, self.modelHist)
                    printTime("  End camShift: ")
                    
                    printTime("  Start compareHist: ")
                    diff = compareHist(frame, roiBoundingBox, self.modelHist)
                    lastArea = roiBoundingBox[2] * roiBoundingBox[3]
                    printTime("  End compareHist: ")
                    
                    if diff > 0.4 and RETECTION_ENABLED:
                        trackingLost = True
                    else:
                        printTime("  Start avgFilter: ")
                        
                        #diffAvg.update(diff)
                        avgFilterX.add(center[0])
                        avgFilterY.add(center[1])
                        
                        xPos = avgFilterX.getAverage()
                        yPos = avgFilterY.getAverage()
                            
                        error = (self.resolution[0]/2-xPos, self.resolution[1]/2-yPos)
                        printTime("  End avgFilter: ")
                        printTime("  Start drawing: ")
                        
                        # HUE: RED=0 -- GREEN=60 -- BLUE=120
                        errorText = text("err=("+str(error[0])+","+str(error[1])+")", (10,self.resolution[1]-10), (0,255,0))
                        diffText = text("diff=("+'{0:.5f}'.format(diff)+")", (150,self.resolution[1]-10), (0,255,0))
                        #stdText = text("mean,std=("+'{0:.5f}'.format(diffAvg.getMeanStd()[0]) + "," +'{0:.5f}'.format(diffAvg.getMeanStd()[1]) + ")", 
                        #                (275,resolution[1]-10), (255,0,0))
                        
                        avgCenterPoint = point('AvgCoords', xPos, yPos, (120,0,0), '('+str(xPos)+','+str(yPos)+')')
                        trueCenterPoint = point('Coordinates', center[0], center[1], (0,255,255), '')
                        
                        overlayTexts = [errorText, diffText]
                        frameRateNum = None
                        if self.showFps:
                            fps = calculateFrameRate(time.time() - startTime)
                            frameRateNum = number('fps', fps, (self.resolution[0]-25,15), (120,0,0))
                        
                        self.drawOverlay(frame,
                                    boxPts=pts,
                                    textToDraw=overlayTexts,
                                    pointsToDraw=[trueCenterPoint, avgCenterPoint],
                                    crossHair=(self.resolution[0]/2, self.resolution[1]/2, 10),
                                    numToDraw=frameRateNum)
                        
                        printTime("  End drawing: ")
                        
                        printTime(" Start showFrame: ")


                        startTime = time.time()
                        
                        self.displayOutput(frame)

                                    
                        printTime(" End showFrame: ")
                else: #Tracking is lost therefore begin running redetectionAlg
                    printTime("  Start redetection: ")
                    redetectRoi = redetectionAlg(frame, self.modelHist, lastArea, 0.4)
                    printTime("  End redetection: ")
                    if redetectRoi is not None:
                        roiBox = redetectRoi
                        trackingLost = False
                        
                    if self.showFps:
                        fps = calculateFrameRate(time.time() - startTime)
                        frameRateNum = number('fps', fps, (self.resolution[0]-25,15), (120,0,0))
                        
                        self.drawOverlay(frame, numToDraw=frameRateNum)
                    
                    startTime = time.time()

                    self.displayOutput(frame)
                    
#                     print "TRACKING LOST " + str(trackingLost) + " fps=" + str(fps)
    
                printTime(" End tracking: ")
                # For matlab analysis
                # fo = open("../../MatlabScripts/diff.txt", 'a')
                # fo.write(str(diff)+'\n')
                
            # show the frame and record if the user presses a key
            else:
                if self.showFps:
                    fps = calculateFrameRate(time.time() - startTime)
                    frameRateNum = number('fps', fps, (self.resolution[0]-25,15), (120,0,0))
                        
                    self.drawOverlay(frame, numToDraw=frameRateNum)
                    
                startTime = time.time()

                self.displayOutput(frame)

#                print "Tracking Off. Press 'i' to initiate. fps=" + str(fps)            
            if DEBUG:
                cv2.imwrite("frame.jpg", frame);
            
            key = cv2.waitKey(1) & 0xFF
    
            # handle if the 'i' key is pressed, then go into ROI
            # selection mode
            if key == ord("i") and len(self.roiPts) < 4:
                # indicate that we are in input mode and clone the
                # frame
                inputMode = True
                
                origFrame = frame.copy()
                
                # keep looping until 4 reference ROI points have
                # been selected; press any key to exit ROI selction
                # mode once 4 points have been selected
                while len(self.roiPts) < 4:
                    cv2.setMouseCallback("frame", self.selectROI, frame)
                    cv2.waitKey(0)
    
                # determine the top-left and bottom-right points
                roiPts = np.array(self.roiPts)
                s = roiPts.sum(axis = 1)
                tl = roiPts[np.argmin(s)]
                br = roiPts[np.argmax(s)]
    
                # grab the ROI for the bounding box and convert it
                # to the HSV color space
                roi = origFrame[tl[1]:br[1], tl[0]:br[0]]
                #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    
                # compute a HSV histogram for the ROI and store the
                # bounding box
                mask  = getHSVMask(roi, LOWER_MASK_BOUND, UPPER_MASK_BOUND)
                self.modelHist = cv2.calcHist([roi], [0], mask, [16], [0, 180])
                self.modelHist = cv2.normalize(self.modelHist, self.modelHist, 0, 255, cv2.NORM_MINMAX)
                
                if DEBUG or self.showHistogram:
                    print self.modelHist
                    cv2.imshow('ModelHistogram', plotHsvHist(self.modelHist))
                
                roiBox = (tl[0], tl[1], br[0], br[1])
                cv2.setMouseCallback("frame", self.selectROI, None)
            # if the 'q' key is pressed, stop the loop
            elif key == ord("q"):
                #print "Quitting"
                break
    
        # cleanup the camera and close any open windows
        #self.camera.release()
        cv2.destroyWindow("frame")
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform Camshift Tracking.\nUsage: \t"i" to select ROI\n\t"q" to exit' , formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('-d','--debug', dest='debug', action='store_const', const=True, default=False, help='enable debug mode. Displays multiple screens and saves .jpg images.')
    parser.add_argument('-filter', dest='avgFilterN', default=10, type=int, help='set length of averaging filter.')
    parser.add_argument('-resolution', dest='res', default=[640, 480], nargs=2, type=int, help='set resolution of camera video capture. usage: -resolution [X] [Y].')
    parser.add_argument('-showFps', dest='showFps', action='store_const', const=True, default=False, help='display fps.')
    parser.add_argument('-displayMode', dest='mode', default='BGR', type=str, help='choose display mode.')
    parser.add_argument('-showHist', dest='showHist', action='store_const', const=True, default=False, help='display fps.')
    args = parser.parse_args()

    debug = args.debug
    showFps = args.showFps
    avgFilterN = args.avgFilterN
    resolution = args.res
    displayMode = args.mode
    showHist = args.showHist
    
    camera = Webcam(resolution)
    processor = ImageProcessor(camera, resolution, avgFilterN)
    time.sleep(1)
    processor.setDebugMode(debug)
    processor.setShowFps(showFps)
    processor.setOutputMode(displayMode)
    processor.setShowHistogram(showHist)
    processor.processImage()
    camera.release()
