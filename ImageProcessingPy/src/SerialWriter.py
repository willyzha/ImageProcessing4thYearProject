import serial
import time
from threading import Thread
from serial.serialutil import SerialException
import platform
import sys

class SerialPort():
    def __init__(self, port, baudRate, timeout, DEBUG=False):
        self.serialPort = serial.Serial(port, baudRate, timeout=timeout)
        time.sleep(1)
        self.runThread = True
        self.ThreadStarted = False
        self.last_received = ""
        self.DEBUG = DEBUG
        Thread(target=self.receiving, args=()).start()
        
    def write(self, text):
    #self.serialPort.open()
        checkSum = self.checkSum(text.strip())
        serialData = str(checkSum) + "*" + text.strip() + "\n"
        #print "send: " + serialData.strip()
        self.serialPort.write(serialData.encode())

    def receiving(self):
        self.ThreadStarted = True
        while self.runThread:
            ## TODO: NEED TO ADD CHECKSUM HERE
            ## AND ALSO FLAG CHECK???
            serialMessage = self.serialPort.readline().strip().decode('utf-8')
            checkSumReceivedStr, serialMessage = serialMessage.split("*")
            checkSumReceived = int(checkSumReceivedStr)
            _, value = serialMessage.split(":")
            checkSumCalc = self.checkSum(value.strip())
            if self.DEBUG:
                print (serialMessage)
            if checkSumReceived == checkSumCalc:
                if "Flag: " in serialMessage:
                    self.last_received = serialMessage
        self.ThreadStarted = False

    def read(self):
        return self.last_received

    def stopThread(self):
        self.runThread = False
        print ('stopping thread')
        while self.ThreadStarted:
            time.sleep(0.001)
        print ('threadStopped')
            
    def close(self):
        self.stopThread()
        self.serialPort.close()

    def checkSum(self,s):
        checksum = 0
        for c in s:
            checksum += ord(c)
        return checksum
    
def main():
    serialport = None
    try:
        OS = platform.system()
        if OS == 'Windows':
            print ('WINDOWS')
            portName = 'COM3'
            serialport = SerialPort(portName, 115200, 2, True)
        elif OS == 'Linux':
            print ('LINUX')
            portName = '/dev/ttyACM0'
            serialport = SerialPort(portName, 115200, 2, True)

        try:
            while True:
                ## CH1 CH2 CH3 CH4
                serialport.write("-1 1000 1000 1000")
                time.sleep(0.0167)
        except KeyboardInterrupt:
            serialport.close()
            pass
    except SerialException:
        print ("Failed to open serial port")
    


if __name__ == '__main__':
    main()
