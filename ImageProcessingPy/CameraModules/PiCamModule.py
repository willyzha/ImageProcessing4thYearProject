import time

from CameraModule import CameraModule
from picamera.array import PiRGBArray
from picamera import PiCamera

class PiCam(CameraModule):
    def __init__(self, resolution):
        time.sleep(0.1)
        self.camera = PiCamera()
        self.camera.resolution = resolution
    
    def getFrame(self):
        rawCapture = PiRGBArray(self.camera)
        self.camera.capture(rawCapture, format="bgr")
        
        frame = rawCapture.array
        
        return (True, frame)