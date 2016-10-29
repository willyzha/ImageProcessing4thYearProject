import cv2
from CameraModule import CameraModule

class Webcam(CameraModule):
    def __init__(self, resolution):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        
    def getFrame(self):
        return self.camera.read()
    
    def release(self):
        self.camera.release()