#include <Servo.h>
// Open a serial connection and flash LED when input is received

int ledRed = 4;      // LED connected to digital pin 4
Servo myservo;  // create servo object to control a servo
Servo yourservo;

void setup(){
 // Open serial connection.
 Serial.begin(9600);
 Serial.setTimeout(1000);
 pinMode(ledRed, OUTPUT);     

  myservo.attach(9, 800, 2350);  // attaches the servo on pin 9 to the servo object
  yourservo.attach(8, 800, 2350);
}

void loop(){
 if(Serial.available() > 0){      // if data present, blink
       String text = Serial.readStringUntil('\n');

       int angle = text.toInt();
       Serial.println(angle);

       //if (angle < 120) {
         myservo.write(angle);
         yourservo.write(angle);
       //}
   }
}
