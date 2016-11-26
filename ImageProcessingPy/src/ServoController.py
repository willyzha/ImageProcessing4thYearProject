import serial
import time

PAN_CENTER = 90
TILT_CENTER = 80
MAX_ANGLE = 145
MIN_ANGLE = 0

class ServoController():
    def __init__(self, port, baudRate, timeout):
        self.port = port
        self.baudRate = baudRate
        self.timeout = timeout
        self.serialPort = serial.Serial(self.port, self.baudRate, timeout=self.timeout)
        self.pan = PAN_CENTER
        self.tilt = TILT_CENTER
        time.sleep(1)
        self.updateServoPosition()

    #def setup(self):
        #self.serialPort = serial.Serial(self.port, self.baudRate, timeout=self.timeout)

    def close(self):
        self.serialPort.close()
        self.serialPort = None
            
    def updatePan(self, step):
        if self.pan+step >= MAX_ANGLE:
            self.pan = MAX_ANGLE
        elif self.pan+step <= MIN_ANGLE:
            self.pan = MIN_ANGLE
        else:
            self.pan = self.pan + step
            
    def setServoPosition(self, panPosition, tiltPosition):
        if(panPosition>= MAX_ANGLE):
            self.pan = MAX_ANGLE
        elif(panPosition<=MIN_ANGLE):
            self.pan = MIN_ANGLE
        else:
            self.pan = panPosition

        if(tiltPosition >= MAX_ANGLE):
            self.tilt = MAX_ANGLE
        elif(tiltPosition <= MIN_ANGLE):
            self.tilt = MIN_ANGLE
        else:
            self.tilt = tiltPosition
            
        
    def updateTilt(self, step):
        if self.tilt+step >= MAX_ANGLE:
            self.tilt = MAX_ANGLE
        elif self.tilt+step <= MIN_ANGLE:
            self.tilt = MIN_ANGLE
        else:
            self.tilt = self.tilt + step
        
    def updateServoPosition(self):
        print str(self.pan), str(self.tilt)
       
        self.serialPort.write(str(self.pan)+" "+ str(self.tilt)+"\n")
    
if __name__ == "__main__":
    servoCtrl = ServoController('/dev/ttyACM0', 9600, 2)
    #servoCtrl.setup()
    angle = 90
    increment = 1;
    servoCtrl.updatePan(50)
    servoCtrl.updateTilt(30)
    servoCtrl.updateServoPosition()
    time.sleep(0.1)    
            
    while True:
        time.sleep(0.01)
        angle = angle + increment
        servoCtrl.updatePan(increment)
        servoCtrl.updateTilt(increment)
        servoCtrl.updateServoPosition()

        if angle <= 0:
            increment = 1
        elif angle >= 145:
            increment = -1
              
