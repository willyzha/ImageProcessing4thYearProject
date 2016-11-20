#include <Servo.h>
// Open a serial connection and flash LED when input is received

int ledRed = 4;      // LED connected to digital pin 4
Servo panServo;  // create servo object to control a servo
Servo tiltServo;

void setup(){
 // Open serial connection.
 Serial.begin(9600);
 Serial.setTimeout(1000);
 pinMode(ledRed, OUTPUT);     

  panServo.attach(9, 500, 2350);  // attaches the servo on pin 9 to the servo object
  tiltServo.attach(8, 500, 2350);
}

void loop(){
 if(Serial.available() > 0){      // if data present, blink
       String text = Serial.readStringUntil('\n');

       int panAngle = text.substring(0, text.indexOf(" ")).toInt();
       int yawAngle = text.substring(text.indexOf(" "), text.indexOf("\n")).toInt();
       //Serial.println(angle);


         panServo.write(panAngle);
         tiltServo.write(yawAngle);

   }
}
