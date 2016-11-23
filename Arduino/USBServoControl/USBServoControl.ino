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
int pan_pos;
int tilt_pos;
const int servo_min = 0;
const int servo_netural = 90;
const int servo_max = 180;

void setup() {
  panservo.attach(9, 500, 2400);  // attaches the servo on pin 9 to the servo object
  panservo.write(servo_netural);
  pan_pos = servo_netural;
  tiltservo.attach(8, 500, 2400);
  tiltservo.write(servo_netural);
  tilt_pos = servo_netural;
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()){
    controlServo(Serial.read()-'0');
  }
}

void controlServo(int n){
  // orientation when facing servo
  switch(n){
    case 1:{
      //look up
      if(servo_min<=tilt_pos-3){
          tilt_pos-=3;
          tiltservo.write(tilt_pos);
      }
    }
    case 2: 
    { //look right
      if(servo_max>=pan_pos+3){
          pan_pos+=3;
          panservo.write(pan_pos);
      }
    }
    case 3:{
      //look down
      if(servo_max<=tilt_pos+3){
          tilt_pos+=3;
          tiltservo.write(tilt_pos);
      }
    }
    case 4:{
      //look left
      if(servo_min<=pan_pos-3){
          pan_pos-=3;
          panservo.write(pan_pos);
      }
    }
    default:{
      //ignore faulty data
    }
  }
}


