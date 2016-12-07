"""
ldr.py
Display analog data from Arduino using Python (matplotlib)
Author: Mahesh Venkitachalam
Website: electronut.in
"""

import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque

import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import re
import time
    
# plot class
class AnalogPlot:
    # constr
    def __init__(self, strPort, maxLen):
        # open serial port
        self.ser = serial.Serial(strPort, 115200)
    
        self.a = {}
        self.ax = deque([0.0]*maxLen)
        self.ay = deque([0.0]*maxLen)
        self.maxLen = maxLen
        self.files = {}
        self.startTime = time.time()
    
    # add to buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)
    
    # add data
    def add(self, key, val):
        #print data
        #assert(len(data) == 2)
        
        if key not in self.a.keys():
            self.a[key] = deque([0.0]*self.maxLen)
            
        self.addToBuf(self.a[key], val)
#         self.addToBuf(self.a[name[0]], data[0])
#         self.addToBuf(self.a[name[1]], data[1])
    
    # update plot
    def update(self, frameNum, a0, a1, an):
        try:
            line = self.ser.readline()#.splitlines()
            #print line
            #names = re.findall("([a-z]+)", line)
            #data = re.findall("(\d+)", line)

            data = dict(x.split(':') for x in line.replace('\r\n', '').split(' '))
            #print data
            for key,val in data.iteritems():
                #print key
                val = float(val)
                self.writeFiles(key,val)
                if key in an.keys():
                    #print key
                    #print an.keys()
                    self.add(key, val)
                    an[key].set_data(range(self.maxLen), self.a[key])
        except KeyboardInterrupt:
            print('exiting')
        except ValueError:
            pass
        
        return
    
    # clean up
    def close(self):
        # close serial
        self.ser.flush()
        self.ser.close()    
    
    def writeFiles(self, key, val):
        currTime = time.time() - self.startTime
        if key in self.files:
            self.files[key].write(str(currTime) +','+ str(val)+'\n')
#                     data[key]['time'].append(ret[key][0])
#                     data[key]['val'].append(ret[key][1])
        else:
            try:
                print "new key:" + key
                self.files[key] = open(key+'.csv', 'w')
            except IOError:
                print key + " is invalid file name."
                return
            self.files[key].write('time,'+key+'\n')
            self.files[key].write(str(currTime) +','+ str(val)+'\n')
    
# main() function
def main():
    # create parser
    parser = argparse.ArgumentParser(description="LDR serial")
    # add expected arguments
    parser.add_argument('--port', dest='port', required=True)
    
    # parse args
    args = parser.parse_args()
    
    #strPort = '/dev/tty.usbserial-A7006Yqh'
    strPort = args.port
    
    print('reading from serial port %s...' % strPort)
    
    # plot parameters
    analogPlot = AnalogPlot(strPort, 100)
    
    print('plotting data...')
    
    # set up animation
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 100), ylim=(0, 1023))
    a0 = 0#ax.plot([], [])
    a1 = 0#ax.plot([], [])
    keys = ['rand', 'testb', 'rand2', 'test2']
    an = {}
    for key in keys:
        an[key], = ax.plot([], [])
    
    anim = animation.FuncAnimation(fig, analogPlot.update, 
                                   fargs=(a0, a1, an), 
                                   interval=50)
    
    # show plot
    plt.show()
    
    # clean up
    analogPlot.close()
    
    print('exiting.')


# call main
if __name__ == '__main__':
    main()