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
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position


void setup() {
  panservo.attach(9, 500, 2400);  // attaches the servo on pin 9 to the servo object
  tiltservo.attach(8, 500, 2400);
}

void loop() {
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
