import serial
import time
from threading import Thread

class SerialPort():
    def __init__(self, port, baudRate, timeout):
        self.serialPort = serial.Serial(port, baudRate, timeout=timeout)
        time.sleep(1)
        self.runThread = True
        self.ThreadStarted = False
        self.last_received = ""
        Thread(target=self.receiving, args=()).start()
        
    def write(self, text):
    #self.serialPort.open()
        
        self.serialPort.write(text)

    def receiving(self):
        self.ThreadStarted = True
        while self.runThread:
            self.last_received = self.serialPort.readline()
            #print(self.last_received)
        self.ThreadStarted = False

    def read(self):
        return self.last_received

    def stopThread(self):
        self.runThread = False
        print 'stopping thread'
        while self.ThreadStarted:
            time.sleep(0.001)
        print 'threadStopped'
            
    def close(self):
        self.stopThread()
        self.serialPort.close()
    
def main():
    port = SerialPort('COM3', 115200, 2)
    test = "100,200,500,600\n"
    try:
        while True:
            port.write(test.encode())
            if "Flag: " in port.read():
                print(port.read().strip())
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        port.close()
        pass

if __name__ == '__main__':
    main()