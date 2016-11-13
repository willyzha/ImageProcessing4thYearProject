import cv2
import time
from CameraModule import CameraModule
from threading import Thread

class Webcam(CameraModule):
    def __init__(self, resolution):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        
        self.stopped = False
        self.grabbed = False
        self.frame = None
        self.start()
        
    def start(self):
        Thread(target=self.update, args=()).start()
        time.sleep(0.1)
        
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