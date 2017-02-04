import cv2
import time
from CameraModule import CameraModule
from threading import Thread

class Webcam(CameraModule):
    def __init__(self, resolution):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.selectFocalLength(resolution)
        self.stopped = False
        self.grabbed = False
        self.frame = None
        self.start()
        
    def start(self):
        Thread(target=self.update, args=()).start()
        time.sleep(2)
        
    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
 
            # otherwise, read the next frame from the stream
            (self.grabbed, frame) = self.camera.read()
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        
    def getFrame(self):
        return (self.grabbed, self.frame)
    
    def release(self):
        self.stopped = True
        time.sleep(0.1)
        self.camera.release()
        
    def getFocalLength(self):
        return self.focalLength
        
    def selectFocalLength(self, resolution):
        # F = (P * D) / H 
        if resolution[0] == 1280 and resolution[1] == 720:
            self.focalLength = (519 * 20)/7.2  # F = (519px * 20cm)/7.2cm
        elif resolution[0] == 640 and resolution[1] == 480:
            self.focalLength = (310 * 20)/7.2  # F = (310px * 20cm)/7.2cm
        else:
            raise ValueError("Unsupported " + str(resolution) +" resolution")
