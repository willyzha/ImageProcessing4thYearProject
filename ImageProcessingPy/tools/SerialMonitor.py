import serial
import time
from threading import Thread
import matplotlib.pyplot as plt
import csv
import cv2

last_received = ''
runTread = False
zeroTime = time.time()

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


def receiving(serial_port):
    global last_received, runTread
    runTread = True
    buff = ''
    while runTread:
        buff += serial_port.read_all()
        if '\n' in buff:
            lines = buff.split('\n')  # Guaranteed to have at least 2 entries
            last_received = lines[-2]
            # If the Arduino sends lots of empty lines, you'll lose the last
            # filled line, so you could make the above statement conditional
            # like so: if lines[-2]: last_received = lines[-2]
            buff = lines[-1]

def plot():
    global runThread
    while runThread:
        pullData = open("rand.csv","r").read()
        dataArray = pullData.split('\n')
        xar = []
        yar = []
        for eachLine in dataArray:
            if len(eachLine)>1:
                x,y = eachLine.split(',')
                xar.append(int(x))
                yar.append(int(y))
        ax1.clear()
        ax1.plot(xar,yar)
        plt.show()
        time.sleep(1)

class SerialData(object):
    def __init__(self, port, baud, timeout):
        try:
            self.serial_port = serial.Serial(port, baud, timeout=timeout)
            print 'Setup Sucess'
        except serial.serialutil.SerialException:
            # no serial connection
            self.serial_port = None
        else:
            Thread(target=receiving, args=(self.serial_port,)).start()

    def next(self):
        if self.serial_port is None:
            # return anything so we can test when Arduino isn't connected
            return None
        # return a float value or try a few times until we get one
        for i in range(40):
            raw_line = last_received
            
            try:
                data = {}
                timeStamp = time.time() - zeroTime
                for d in raw_line.split():
                    key = d.split(':')[0]
                    val = d.split(':')[1]
                    data[key] = (timeStamp, val)
                
                #data['time'] = timeStamp
                return data
            except ValueError:
                time.sleep(.005)
        return None

    def __del__(self):
        if self.serial_port is not None:
            self.serial_port.close()

if __name__ == '__main__':
    s = SerialData('COM3', 115200, timeout=1) # port=/dev/ttyS[0123] for raspberry pi
    #plt.ion()
    plot = False
    data = {}
    files = {}
    Thread(target=plot).start()
    try:
        while True:#for i in range(500):
            time.sleep(0.01)
            ret = s.next()
            if ret is not None:
                for key in ret.keys():
                    if key in files:
                        files[key].write(str(ret[key][0]) +','+ str(ret[key][1])+'\n')
    #                     data[key]['time'].append(ret[key][0])
    #                     data[key]['val'].append(ret[key][1])
                    else:
                        print "new key:" + key
                        files[key] = open(key+'.csv', 'w')
                        files[key].write('time,'+key+'\n')
                        files[key].write(str(ret[key][0]) +','+ str(ret[key][1])+'\n')
#                     data[key] = {'time':[ret[key][0]], 'val':[ret[key][1]]}
    except KeyboardInterrupt:
        pass

#     w = csv.writer(open("temp.csv", "w"))
#     for key, val in data.items():
#         w.writerow([key, val])
#         
#     print data
    
    runTread = False
    print "done!"