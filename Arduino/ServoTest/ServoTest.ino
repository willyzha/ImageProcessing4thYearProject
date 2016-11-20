/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
Servo yourservo;
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  myservo.attach(9, 500, 2400);  // attaches the servo on pin 9 to the servo object
  yourservo.attach(8, 500, 2400);
}

void loop() {
  for (pos = 0; pos <= 180; pos += 60) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    yourservo.write(pos);
    delay(100);                       // waits 15ms for the servo to reach the position
  }
  for (pos = 180; pos >= 0; pos -= 20) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    yourservo.write(pos);
    delay(100);                       // waits 15ms for the servo to reach the position
  }
}
