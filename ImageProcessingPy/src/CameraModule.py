class CameraModule:
    def __init__(self, resolution):
        self.resolution = resolution
        
    def getFrame(self):
        raise NotImplementedError("getFrame is an abstract method.")