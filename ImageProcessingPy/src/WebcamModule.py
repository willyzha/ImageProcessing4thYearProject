import cv2
from CameraModule import CameraModule

class Webcam(CameraModule):
    def __init__(self, resolution):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        
    def getFrame(self):
    	grabbed, frame = self.camera.read()
    	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return (grabbed, hsv)
    
    def release(self):
        self.camera.release()