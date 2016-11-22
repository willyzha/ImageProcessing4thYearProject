import time

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2

class PiCam:
    def __init__(self, resolution):
        time.sleep(0.1)
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False
        self.start()
        self.calibrateWhiteBalance()
    
    def start(self):
        Thread(target=self.update, args=()).start()
        time.sleep(0.5)

    def update(self):
        for f in self.stream:
            self.frame = cv2.cvtColor(f.array, cv2.COLOR_BGR2HSV)
            self.rawCapture.truncate(0)
            
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
    def calibrateWhiteBalance(self):
        self.camera.awb_mode = 'off'
        rg,bg = (0.5, 0.5)
        self.camera.awb_gains = (rg, bg)
        with PiRGBArray(self.camera, size=(128, 72)) as output:
        # Allow 30 attempts to fix AWB
            for i in range(30):
                # Capture a tiny resized image in RGB format, and extract the
                # average R, G, and B values
                self.camera.capture(output, format='rgb', resize=(128, 72), use_video_port=True)
                r, g, b = (np.mean(output.array[..., i]) for i in range(3))
                print('R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)' % (
                    rg, bg, r, g, b))
                # Adjust R and B relative to G, but only if they're significantly
                # different (delta +/- 2)
                if abs(r - g) > 2:
                    if r > g:
                        rg -= 0.1
                    else:
                        rg += 0.1
                if abs(b - g) > 1:
                    if b > g:
                        bg -= 0.1
                    else:
                        bg += 0.1
                self.camera.awb_gains = (rg, bg)
                output.seek(0)
                output.truncate()
        print 'calibration is completed'
        if (abs(r - g) > 2) and (abs(b - g) > 1):
            # whitebalance is failed, manual white balance is aborted and auto awb is set
            print 'calibration was not successful'
            self.camera.awb_mode='auto'

    def getFrame(self):
        frame = self.frame        
        return (True, frame)

    def release(self):
        self.stopped = True
        time.sleep(1)
