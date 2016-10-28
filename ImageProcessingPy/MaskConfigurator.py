import cv2
import numpy as np

global Hmin, Smin, Vmin, Hmax, Smax, Vmax

def setMinValues(event):
    global Hmin, Smin, Vmin
    Hmin = cv2.getTrackbarPos("hueMin", "configurator")
    Smin = cv2.getTrackbarPos("satMin", "configurator")
    Vmin = cv2.getTrackbarPos("valMin", "configurator")
    
def setMaxValues(event):
    global Hmax, Smax, Vmax
    Hmax = cv2.getTrackbarPos("hueMax", "configurator")
    Smax = cv2.getTrackbarPos("satMax", "configurator")
    Vmax = cv2.getTrackbarPos("valMax", "configurator")
    
def getHSVMask(frame, lowerb, upperb):
    print lowerb
    print upperb
    if lowerb[0] < upperb[0]:
        return cv2.inRange(frame, lowerb, upperb)
    else:
        temp = list(upperb)
        temp[0] = 255
        mask1 = cv2.inRange(frame, lowerb, tuple(temp))
        temp = list(lowerb)
        temp[0] = 0
        mask2 = cv2.inRange(frame, tuple(temp), upperb)
        return cv2.bitwise_or(mask1, mask2)
    
def main():
    global Hmin, Smin, Vmin, Hmax, Smax, Vmax

    Hmin = 238
    Smin = 107
    Vmin = 13
    Hmax = 8
    Smax = 255
    Vmax = 255

    camera = cv2.VideoCapture(0)
    
    # setup the mouse callback
    cv2.namedWindow("frame")
    cv2.namedWindow("configurator")
    cv2.createTrackbar("hueMin", "configurator", Hmin, 255, setMinValues)
    cv2.createTrackbar("satMin", "configurator", Smin, 255, setMinValues)
    cv2.createTrackbar("valMin", "configurator", Vmin, 255, setMinValues)

    cv2.createTrackbar("hueMax", "configurator", Hmax, 255, setMaxValues)
    cv2.createTrackbar("satMax", "configurator", Smax, 255, setMaxValues)
    cv2.createTrackbar("valMax", "configurator", Vmax, 255, setMaxValues)

    # keep looping over the frames
    while True:
        (grabbed, frame) = camera.read()
        
        # check to see if we have reached the end of the
        # video
        if not grabbed:
            print "Could not read from camera exiting..."
            break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask = getHSVMask(hsv, (Hmin, Smin, Vmin), (Hmax, Smax, Vmax))
        kernel = np.ones((3,3),np.uint8)
        mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel)
        
        # show the frame and record if the user presses a key
        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):
            cv2.imwrite("frame.jpg", frame)
            cv2.imwrite("mask.jpg", mask)
            print "Quitting..."
            break

if __name__ == "__main__":
    main()