/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo panservo;  // create pan (horizontal) servo object
Servo tiltservo; // create tilt (vertical) servo object

const int pan_min = 15;
const int pan_neutral = 90;
const int pan_max = 165;
const int tilt_min = 0;
const int tilt_neutral = 90;
const int tilt_maxt = 180;

int pos = 0;    // variable to store the servo position


void setup() {
  panservo.attach(9, 500, 2400);  // attaches the servo on pin 9 to the servo object
  tiltservo.attach(8, 500, 2400);
}

void loop() {
  panservo.write(0);
  tiltservo.write(0);
  delay(5000);
  panservo.write(10);
  delay(5000);
  for (pos = 0; pos <= 180; pos += 20) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    panservo.write(pos);              // tell servo to go to position in variable 'pos'
    tiltservo.write(pos);
    delay(100);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 180; pos >= 0; pos -= 20) { // goes from 180 degrees to 0 degrees
    panservo.write(pos);              // tell servo to go to position in variable 'pos'
    tiltservo.write(pos);
    delay(100);                       // waits 15ms for the servo to reach the position
  }
}
