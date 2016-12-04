import numpy as np
import argparse
import cv2
from _collections import deque
from collections import namedtuple
from WebcamModule import Webcam
import time
from math import sqrt
from HistogramPlotter import plotHsvHist
from ServoController import ServoController
from threading import Thread

# initialize the current frameHsv of the video, along with the list of
# ROI points along with whether or not this is input mode
inputMode = False
TIME_ANALYSIS = False

# SELECT OPTIMIZED VALUES WITH MaskConfigurator or PiMaskConfigurator
LOWER_MASK_BOUND = np.array([0,40,90])
UPPER_MASK_BOUND = np.array([255,255,255])

# ENABLE/DISABLE TRACKING HALTING AND REDETECTION
RETECTION_ENABLED = False

text = namedtuple('text', ['text', 'origin', 'color'])
point = namedtuple('point', ['name', 'x', 'y', 'color', 'text'])
number = namedtuple('number', ['name', 'val', 'origin', 'color'])

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
    
    def getThreshold(self, nrStd):
        return self.mean + nrStd * self.std
    
    def inRange(self, data, nrStd):
        # For best results this should be checked before calling update
        if self.count > 100:
            return data <= self.getThreshold(nrStd)
        else:
            return True
        
    def reset(self):
        self.count = 0
        self.mean = 0
        self.std = 0
    
def compareHist(frame, roiWindow, refHist, lowerb, upperb):  
    """ Compares the histogram of the roiWindow in frameHsv with refHist
    """

    # Get the submatrix for the region of interest and convert to HSV
    roi = frame[roiWindow[1]:roiWindow[1]+roiWindow[3], roiWindow[0]:roiWindow[0]+roiWindow[2]]

    #roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
   
    # Use the same mask from the original histogram generation
    mask  = cv2.inRange(roi, lowerb, upperb)
    
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

def calculateFrameRate(deltaT):
    if deltaT == 0:
        return -1
    return int(round(1/deltaT))

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
        self.servoEnabled = False
        self.debug = False
        
        self.diffAvgStd = RunningAvgStd()
        
        self.selection = None
        self.drag_start = None
        # If 0 then currently ROI selection, 1 then tracking
        self.tracking_state = 0
        self.show_backproj = False
        
        self.frameHsv = None
        
    def onmouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y]) # BUG

        if self.tracking_state:
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.tracking_state = 0
            return
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                h, w = self.frameHsv.shape[:2]
                xo, yo = self.drag_start
                x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y]))
                x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y]))
                self.selection = None
                if x1-x0 > 0 and y1-y0 > 0:
                    self.selection = (x0, y0, x1, y1)
                    self.roiPts = self.selection 
            else:
                self.drag_start = None
                if self.selection is not None:
                    self.tracking_state = 1
                    
    def redetectionAlg(self, aFrame, aRoiHist, aLastArea, aDiffThresh, lowerb, upperb):
        """ Algorithm for redetecting the object after it is lost
            Inputs:
                aFrame: Frame in which the object is to be searched for
                aRoiHist: The pre-calculated Hue histogram for the object of interest
                aLastArea: The area of ROI of the object when last seen
                aDiffThresh: Min difference threshold to determine the object is found
            Outputs: 
                matchedRect: Most probable rectangle around object. None if no matches were found
        """
        
        if aRoiHist is None:
            return
        
        # Step1: Find HSV back projection of the frameHsv
        #hsv = cv2.cvtColor(aFrame, cv2.COLOR_BGR2HSV)
        hsv = aFrame
        backProj = cv2.calcBackProject([hsv], [0], aRoiHist, [0, 180], 1)
        mask = cv2.inRange(hsv, lowerb, upperb)
        backProj &= mask
        
        # Step2: Binarize Back Projection
        _, threshold = cv2.threshold(backProj, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
           
        # Step3: Erode and Dilate
        kernel = np.ones((5,5),np.uint8)
        maskedThresh = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
    
        # NOTE WZ: can try cv2.CHAIN_APPROX_NONE for no approximation
        _, contours, _ = cv2.findContours(maskedThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
             
        # Step4: Find candidate regions with appropriate size of 30%
        candidateEllipse = []
        largestArea = 0
        for contour in contours: 
            if len(contour) < 5:
                continue
            ellipse = cv2.fitEllipse(contour)
            area = ellipse[1][0] * ellipse[1][1] * 3.14
            if area > largestArea:
                largestArea = area
                
            if area >= (aLastArea * 0.5):
                candidateEllipse.append(ellipse)
        
        #print largestArea, aLastArea * 0.3        
        
        if self.debug:
            cv2.imshow("threshold", threshold)
            cv2.imshow("maskedThresh", maskedThresh)
            allContoursFrame = hsv.copy()
            cv2.drawContours(allContoursFrame, contours, -1, (0, 255,0), 2)
            for el in candidateEllipse:
                cv2.ellipse(allContoursFrame, el, (0, 0, 255), 2)
            cv2.imshow("allContoursFrame", allContoursFrame)
    
        # Step5: Look through candidate contours and select the one with lowest diff that is below the diff threshold
        matchedRect = None
        minDiff = 1 # max diff is 1
        for ellipse in candidateEllipse:
            boundingRect = cv2.boundingRect(cv2.boxPoints(ellipse))
            print boundingRect 
            diff = compareHist(aFrame, boundingRect, aRoiHist, lowerb, upperb)
    
            print "diff " + str(diff) + "diffThresh " + str(aDiffThresh)
    
            if diff < aDiffThresh and diff < minDiff:
                minDiff = diff
                matchedRect = boundingRect
    
        return matchedRect

    def resetImageProcessing(self):
        self.tracking_state = 0
        self.modelHist = None
        self.diffAvgStd.reset()
        
    def endImageProcessing(self):
        self.capturing = False
        self.resetImageProcessing()
        cv2.destroyAllWindows()
        
    def quitImageProcessing(self):
        self.endImageProcessing()
        self.camera.release()
        
    def setOutputMode(self, val):
        print val
        if val == "BGR":
            self.outputMode = "BGR"
        elif val == "HSVpure":
            self.outputMode = "HSVpure"         
        elif val == "BackProj":
            self.outputMode = "BackProj" 
        elif val == "None":
            self.outputMode = "None" 
        else:
            raise Exception("Not a valid output configuration!!")

    def setDebugMode(self, d):
        """ Enables debugging for the tracker
        """
        self.debug = d

    def setShowHistogram(self, h):
        self.showHistogram = h
        if h:
            if self.modelHist is not None:
                self.show_hist()
        else:
            cv2.destroyWindow('hist')

    def adjustServo(self, targetPoint):
        center = (self.resolution[0]/2, self.resolution[1]/2)
        
        dX = targetPoint[0] - center[0]
        dY = targetPoint[1] - center[1]

        if dX > 10:
            self.servoCtrl.updatePan(1)
        elif dX < -10:
            self.servoCtrl.updatePan(-1)
            
        if dY > 10:
            self.servoCtrl.updateTilt(-1)
        elif dY < -10:
            self.servoCtrl.updateTilt(1)
            
        self.servoCtrl.updateServoPosition()

    def setShowFps(self, showFps):
        self.showFps = showFps

    def setServo(self, enableServos):
        if enableServos is True and self.servoEnabled is False:
            try:
                self.servoCtrl = ServoController('COM3', 9600, 2)
                self.servoEnabled = enableServos
            except ValueError:
                print "Failed to setup serial port!"
                self.servoCtrl = None
        elif enableServos is False and self.servoEnabled is True:
            self.servoCtrl = None
            self.servoEnabled = enableServos

    def getDebug(self):
        return self.debug

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
            cv2.imshow("frameHsv", cv2.cvtColor(param,cv2.COLOR_HSV2BGR))

    def convertFrame(self, aFrame, mask):
        if self.outputMode is "BGR":
            return cv2.cvtColor(aFrame, cv2.COLOR_HSV2BGR)
        elif self.outputMode is "HSVpure":
            aFrame[:,:,2] = 255
            aFrame[:,:,1] = 255
            return cv2.cvtColor(aFrame, cv2.COLOR_HSV2BGR)
        elif self.outputMode is "BackProj":
            if self.modelHist is None:
                return aFrame
            else:
                return cv2.calcBackProject([aFrame], [0], self.modelHist, [0, 180], 1) & mask
            
        cv2.waitKey(1)

    def drawOverlay(self, targetFrame,crossHair=None, boxPts=None, textToDraw=[], pointsToDraw=[], numToDraw=None):
        """ Draws crossHair, boxes, text and points on the targetFrame
            WARNING: DO NOT DRAW ON PROCESSING FRAME!!!
        """
        if self.outputMode is "None" or self.debug:
            outputText = ""
            for point in pointsToDraw:
                outputText = outputText + point.name+ "="  + point.text + " "
            
            for text in textToDraw:
                outputText = outputText + text.text + " "
                
            if numToDraw is not None:
                outputText = outputText + numToDraw.name + "=(" + str(numToDraw.val) + ")"
            
            print outputText

        if self.outputMode is not "None" or self.debug:
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
                cv2.putText(targetFrame, text=point.text, org=(int(point.x),int(point.y)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.5, 
                    color=point.color,thickness=1, lineType=cv2.LINE_AA)
                cv2.circle(targetFrame,(int(point.x),int(point.y)),2,point.color,thickness=3)

    def show_hist(self):
        bin_count = self.modelHist.shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count*bin_w, 3), np.uint8)
        for i in xrange(bin_count):
            h = int(self.modelHist[i])
            cv2.rectangle(img, (i*bin_w+2, 255), ((i+1)*bin_w-2, 255-h), (int(180.0*i/bin_count), 255, 255), -1)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('hist', img)

    def processImage(self):
        self.capturing = True
        
        cv2.namedWindow('camshift')
        cv2.setMouseCallback('camshift', self.onmouse, self.frameHsv)
        
        targetLost = False
        track_box = None
        
        
        while self.capturing:
            startTime = time.time()
            ret, self.frameHsv = self.camera.getFrame()
            lowerb = np.array((0., 50., 32.))
            upperb = np.array((180., 255., 255.))
            mask = cv2.inRange(self.frameHsv, lowerb, upperb)
            vis = self.convertFrame(self.frameHsv.copy(), mask)
            #hsv = cv2.cvtColor(self.frameHsv, cv2.COLOR_BGR2HSV)

            
            # calculate histogram
            if self.selection:
                targetLost = False
                x0, y0, x1, y1 = self.selection
                self.track_window = (x0, y0, x1-x0, y1-y0)
                hsv_roi = self.frameHsv[y0:y1, x0:x1]
                mask_roi = mask[y0:y1, x0:x1]
                hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
                cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
                self.modelHist = hist.reshape(-1)
                if self.showHistogram:
                    self.show_hist()

                vis_roi = vis[y0:y1, x0:x1]
                cv2.bitwise_not(vis_roi, vis_roi)
                vis[mask == 0] = 0

            if targetLost:
                print track_box
                lastArea = track_box[1][0] * track_box[1][1] * 3.14
                redetectedRoi = self.redetectionAlg(self.frameHsv, self.modelHist, lastArea, self.diffAvgStd.getThreshold(3), lowerb, upperb)
                if redetectedRoi is not None:
                    self.track_window = redetectedRoi
                    targetLost = False
            # Track object
            elif self.tracking_state == 1:
                self.selection = None
                # calculate back projected image
                prob = cv2.calcBackProject([self.frameHsv], [0], self.modelHist, [0, 180], 1)
                prob &= mask
                
                #set termination criteria and find new object location
                term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
                track_box, self.track_window = cv2.CamShift(prob, self.track_window, term_crit)
                
                diff = compareHist(self.frameHsv, self.track_window, self.modelHist, lowerb, upperb)
                print self.diffAvgStd.getThreshold(3), self.diffAvgStd.inRange(diff, 3)
                print "area= " + str(track_box[1][0] * track_box[1][1] * 3.14)
                self.diffAvgStd.update(diff)
                if not self.diffAvgStd.inRange(diff, 3):
                    print "target lost"
                    targetLost = True

                if self.show_backproj:
                    vis[:] = prob[...,np.newaxis]
                try:
                    cv2.ellipse(vis, track_box, (0, 0, 255), 2)
                except:
                    print(track_box)
                
                center = track_box[0]
                centerPoint = point('Coordinates', center[0], center[1], (255,0,0), '('+str(center[0])+','+str(center[1])+')')
                diffText = text("diff=("+'{0:.5f}'.format(diff)+")", (150,self.resolution[1]-10), (0,255,0))
                
                frameRateNum = None
                if self.showFps:
                    fps = calculateFrameRate(time.time() - startTime)
                    frameRateNum = number('fps', fps, (self.resolution[0]-25,15), (120,0,0))
        
                self.drawOverlay(vis, 
                                 crossHair=(self.resolution[0]/2, self.resolution[1]/2, 10), 
                                 boxPts=None, 
                                 textToDraw=[diffText], 
                                 pointsToDraw=[centerPoint], 
                                 numToDraw=frameRateNum)

            if self.outputMode is not "None" and vis is not None:
                cv2.imshow("camshift", vis)

                ch = 0xFF & cv2.waitKey(1)
                if ch == 27:
                    break
                if ch == ord('b'):
                    self.show_backproj = not self.show_backproj
        cv2.destroyWindow('camshift')
   
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform Camshift Tracking.\nUsage: \t"i" to select ROI\n\t"q" to exit' , formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('-d','--debug', dest='debug', action='store_const', const=True, default=False, help='enable debug mode. Displays multiple screens and saves .jpg images.')
    parser.add_argument('-filter', dest='avgFilterN', default=10, type=int, help='set length of averaging filter.')
    parser.add_argument('-resolution', dest='res', default=[640, 480], nargs=2, type=int, help='set resolution of camera video capture. usage: -resolution [X] [Y].')
    parser.add_argument('-showFps', dest='showFps', action='store_const', const=True, default=False, help='display fps.')
    parser.add_argument('-displayMode', dest='mode', default='BGR', type=str, help='choose display mode.')
    parser.add_argument('-showHist', dest='showHist', action='store_const', const=True, default=True, help='display fps.')
    args = parser.parse_args()

    debug = args.debug
    showFps = args.showFps
    avgFilterN = args.avgFilterN
    resolution = args.res
    displayMode = args.mode
    showHist = args.showHist
    
    camera = Webcam(resolution)
    processor = ImageProcessor(camera, resolution, avgFilterN)
    processor.setDebugMode(debug)
    processor.setShowFps(showFps)
    processor.setOutputMode(displayMode)
    processor.setShowHistogram(showHist)
    processor.processImage()
    camera.release()
