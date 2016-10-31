class CameraModule:
    """ Interface for camera modules used to get images 
    """
    def __init__(self, resolution):
        self.resolution = resolution
        
    def getFrame(self):
        raise NotImplementedError("getFrame is an abstract method.")