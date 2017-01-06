import serial
import time
from threading import Thread

class SerialPort():
	def __init__(self, port, baudRate, timeout):
		self.serialPort = serial.Serial(port, baudRate, timeout=timeout)
		time.sleep(1)
		self.runTread = True
		self.last_received = ""
		Thread(target=self.receiving, args=(self.serial_port,)).start()
        
	def write(self, text):
        #self.serialPort.open()
        
		self.serialPort.write(text)
		
	def receiving(self):
		while self.runTread:
			buff += self.serialPort.read_all()
			if '\n' in buff:
				lines = buff.split('\n')  # Guaranteed to have at least 2 entries
				self.last_received = lines[-2]
				# If the Arduino sends lots of empty lines, you'll lose the last
				# filled line, so you could make the above statement conditional
				# like so: if lines[-2]: last_received = lines[-2]
				buff = lines[-1]

	def read(self):
		return self.last_received

def main():
    port = SerialPort('COM3', 9600, 2)
    port.write("FR_MOTOR 100, FL_MOTOR 200, BR_MOTOR 500, BL_MOTOR 600")
    print(port.read())
    

if __name__ == '__main__':
    main()
