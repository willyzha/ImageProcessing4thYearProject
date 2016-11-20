import serial
import time

class SerialPort():
    def __init__(self, port, baudRate, timeout):
        self.serialPort = serial.Serial(port, baudRate, timeout=timeout)
        time.sleep(1)
        
    def write(self, text):
        #self.serialPort.open()
        
        self.serialPort.write(text)
        #self.serialPort.close()
    
if __name__ == "__main__":
    port = SerialPort('COM3', 9600, 2)
    angle = 0
    increment = 10;
    while True:
        print "sending " + str(angle)
        port.write(str(angle) + " " + str(angle)+"\n")
        time.sleep(0.1)
        angle = angle + increment
        if angle <= 0:
            increment = 10
        elif angle >= 180:
            increment = -10