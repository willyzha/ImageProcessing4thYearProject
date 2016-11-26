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
        self.camera.vflip = True
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        self.frame = None
        self.stopped = False
        self.start()
    
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

    def getFrame(self):
        frame = self.frame        
        return (True, frame)

    def release(self):
        self.stopped = True
        time.sleep(1)
