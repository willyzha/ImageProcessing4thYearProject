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
        checkSum = self.checkSum(text)
        serialData = str(checkSum) + "*" + text + "\n"
        self.serialPort.write(serialData.encode())

    def receiving(self):
        self.ThreadStarted = True
        print("Anything")
        while self.runThread:
            self.last_received = self.serialPort.readline()
            print("Last Line: " + str(self.last_received))

    def read(self):
        return self.last_received

    def stopThread(self):
        self.runThread = False
        while self.ThreadStarted:
            time.sleep(0.001)

    def checkSum(self, s):
        sum = 0
        for c in s:
            #print(c)
            sum += ord(c)
        #print(sum)
        return sum

def main():
    port = SerialPort('COM3', 115200, 2)
        test ="100, 200, 500, 600"
        try:
            while True:
                port.write(test)
                #if "Flag: " in port.read():
                #print(port.read())
        except KeyboardInterrupt:
            port.stopThread()
            pass

if __name__ == '__main__':
    main()
