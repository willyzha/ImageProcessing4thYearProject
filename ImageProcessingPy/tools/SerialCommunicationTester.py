import serial
import time

class SerialPort():
    def __init__(self, port, baudRate, timeout):
        self.serialPort = serial.Serial(port, baudRate, timeout=timeout)
        time.sleep(1)
        
    def write(self, text):
        #self.serialPort.open()
        
        self.serialPort.write(text)

    def read(self):
        return self.serialPort.readline()

def main():
    port = SerialPort('COM3', 9600, 2)
    port.write("FR_MOTOR 100, FL_MOTOR 200, BR_MOTOR 500, BL_MOTOR 600")
    print port.read()
    

if __name__ == '__main__':
    main()
