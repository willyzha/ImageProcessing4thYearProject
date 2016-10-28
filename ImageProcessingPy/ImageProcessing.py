import numpy as np
import argparse
import cv2
from _collections import deque

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
    lowerb = np.array([0,100,5])
    upperb = np.array([255,255,255])
    mask = getHSVMask(hsv, lowerb, upperb)
    kernel = np.ones((3,3),np.uint8)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel)
    
    
    backProj = cv2.calcBackProject([hsv], [0], aRoiHist, [0, 180], 1)
    backProj = cv2.morphologyEx(backProj,cv2.MORPH_OPEN, kernel)
    newBackProj = cv2.bitwise_and(backProj, mask)
    # apply cam shift to the back projection, convert the
    # points to a bounding box, and then draw them
    newBackProj = cv2.medianBlur(newBackProj, 5)
     
    (r, aRoiBox) = cv2.CamShift(newBackProj, aRoiBox, termination)
    pts = np.int0(cv2.boxPoints(r))
    cv2.polylines(aFrame, [pts], True, (0, 255, 0), 2)
    
    center = np.uint16(np.around(r[0]))
    cv2.circle(aFrame,(center[0],center[1]),2,(0,0,255),3)

    x, y, width, height = cv2.boundingRect(pts)
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    
    roi = newBackProj[y:y+height, x:x+width]
    
    if DEBUG:
        cv2.imshow("mask", mask)
        cv2.imshow("backProj", backProj)
        cv2.imshow("newBackProj", newBackProj) 
        cv2.imshow("roi",roi)   
        cv2.imwrite("newBackProj.jpg", newBackProj)
    
        print center
    
    return (center, aRoiBox)

def main(avgFilterN):
    global roiPts, inputMode
    camera = cv2.VideoCapture(0)

    # setup the mouse callback
    cv2.namedWindow("frame")

    roiBox = None
    roiHist = None
    
    avgFilterX = AveragingFilter(avgFilterN)
    avgFilterY = AveragingFilter(avgFilterN)

    # keep looping over the frames
    while True:
        # grab the current frame
        (grabbed, frame) = camera.read()
        
        # check to see if we have reached the end of the
        # video
        if not grabbed:
            print "Could not read from camera exiting..."
            break

        # if the see if the ROI has been computed
        if roiBox is not None and roiHist is not None:
            (center, roiBox) = camShiftTracker(frame, roiBox, roiHist)
            avgFilterX.add(center[0])
            avgFilterY.add(center[1])
                        
            cv2.circle(frame,(avgFilterX.getAverage(),avgFilterY.getAverage()),2,(255,0,0),3)
        

        # show the frame and record if the user presses a key
        cv2.imshow("frame", frame)
        cv2.imwrite("frame.jpg", frame);
        
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
            lowerb = np.array([231,124,25])
            upperb = np.array([18,255,255])
            mask  = getHSVMask(roi, lowerb, upperb)
            roiHist = cv2.calcHist([roi], [0], mask, [16], [0, 180])
            roiHist = cv2.normalize(roiHist, roiHist, 0, 255, cv2.NORM_MINMAX)
            
            if DEBUG:
                print roiHist
            
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
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform Camshift Tracking.\nUsage: \t"i" to select ROI\n\t"q" to exit' , formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('-d','--debug', dest='DEBUG', action='store_const', const=True, default=False, help='enable debug mode. Displays multiple screens and saves .jpg images.')
    parser.add_argument('-filter', dest='avgFilterN', default=10, type=int)
    args = parser.parse_args()
    
    DEBUG = args.DEBUG
    avgFilterN = args.avgFilterN
    main(avgFilterN)
    
