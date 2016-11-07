import serial
import time

class SerialPort():
    def __init__(self, port, baudRate, timeout):
        self.serialPort = serial.Serial(port, baudRate, timeout=timeout)
        time.sleep(1)
        
    def write(self, text):
        #self.serialPort.open()
        
        self.serialPort.write(b'hello serial')
        #self.serialPort.close()
    
if __name__ == "__main__":
    port = SerialPort('COM3', 9600, 2)
    
    while True:
        print "sending"
        port.write("hello\n")
        time.sleep(0.5)    