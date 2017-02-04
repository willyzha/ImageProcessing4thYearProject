import sys
import time
sys.path.insert(0, '../src')

from PIDContoller import PID

PID_UT = PID(P=1.6, I=0.0, D=0)
#PID_UT.setSampleTime(0.1)

feedback = 0

while (True): 
    time.sleep(0.5)
    PID_UT.SetPoint = 1
    PID_UT.update(feedback)
    output = PID_UT.output
    feedback = feedback + output
    print feedback, output