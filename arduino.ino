#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050.h"
#include <ArduinoJson.h>
#include <Servo.h>

Servo myservo;
int pos = 0;

MPU6050 mpu;
int16_t ax, ay, az;
int16_t gx, gy, gz;

struct MyData {
  byte X;
  byte Y;
  byte Z;
};

MyData position;

int threshold = 80; // Threshold value for fall detection
int speed = 0;

int age = 65;
int maxHeartRate = 220 - age;

int pirPin = 7;
int LED_Red = 8;
int LED_Yellow = 9;
int LED_Blue = 10;
int Buzzer = 11;

int red_state = 1;
int yellow_state = 1;
int green_state = 1;

int fan = 0;

bool auto_mode = true;

// --- //

unsigned long previousMillis = 0;
const long interval = 1000; // Interval between alarm patterns in milliseconds

// Alarm sound frequencies
const int freqLow = 400;
const int freqMid = 800;
const int freqHigh = 1600;

// Alarm durations
const int shortDuration = 100;
const int longDuration = 300;



void setup() {
  Serial.begin(9600); 

  myservo.attach(3);
  
  pinMode(LED_Red,OUTPUT);
  pinMode(LED_Yellow,OUTPUT);
  pinMode(LED_Blue,OUTPUT);
  pinMode(Buzzer,OUTPUT);
  
  pinMode(pirPin, INPUT);
  Wire.begin();
  mpu.initialize();
}

void updateSetting(){
  
  while(Serial.available() > 0){
    // int income = Serial.read();
    String jsonData = Serial.readString();
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, jsonData);

//     Serial.println("received: " + jsonData);

    if(!error){ 
      if(doc.containsKey("ag")){
        age = doc["ag"];
        threshold = doc["f"];
        red_state = doc["r"];
        yellow_state = doc["y"];
        green_state = doc["g"];
        auto_mode = doc["a"];
        fan = doc["s"];
      }
      
    }
    // else{
      // Serial.println("Error parsing JSON");
    // }
  }
  
}

 
void rotateFan(int fanLevel) {
  int rotations; // declare a variable to store the number of rotations
  switch (fanLevel) {
    case 0:
      rotations = 0; // set the number of rotations to 1 for fan level 1
      break;
    case 1:
      rotations = 1; // set the number of rotations to 1 for fan level 1
      break;
    case 2:
      rotations = 2; // set the number of rotations to 2 for fan level 2
      break;
    case 3:
      rotations = 3; // set the number of rotations to 3 for fan level 3
      break;
  }
  
  for (int i = 0; i < rotations; i++) { // loop through the specified number of rotations
    myservo.write(0); // set the servo to position 0 degrees
    delay(500); // wait for 500ms
    myservo.write(180); // set the servo to position 180 degrees
    delay(500); // wait for 500ms
  }
  
  
}

void loop() {
  
 
  

  rotateFan(fan);
  digitalWrite(LED_Red, red_state);
  digitalWrite(LED_Yellow, yellow_state);
  digitalWrite(LED_Blue, green_state);
  
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  position.X = map(ax, -17000, 17000, 0, 255 );
  position.Y = map(ay, -17000, 17000, 0, 255);
  position.Z = map(az, -17000, 17000, 0, 255);

  updateSetting();
  
  int potA0 = analogRead(A0);
  int potA1 = analogRead(A1);
  bool motionDetect = false;
  bool fallDetect = false;
  
  float temperature = map(potA0, 0, 1023, 0, 100);
  float heartRate = map(potA1, 0, 1023, 0, maxHeartRate);

  if(digitalRead(pirPin) == HIGH){
      motionDetect = true;
  }else{
    motionDetect = false;
  }

  if (az < threshold) {
    fallDetect = true;
  } else {
    fallDetect = false;
  }

  if (auto_mode && fallDetect) {
    alarmPattern();
  }else{
    noTone(Buzzer);
  }

  String data = "{\"temperature\":" + String(temperature) + 
                ",\"heart_rate\":" + String(heartRate) + 
                ",\"motion_detect\":" + motionDetect +
                ",\"fall_detect\":" + fallDetect + 
                ",\"x\":" + position.X + 
                ",\"y\":" + position.Y + 
                ",\"z\":" + position.Z + "}";

  Serial.println(data);


  
  delay(1000); // wait for a short period before reading the sensor again
}

void alarmPattern() {
  // First pattern: two short beeps
  tone(Buzzer, freqMid, shortDuration);
  delay(shortDuration * 2);
  tone(Buzzer, freqMid, shortDuration);
  delay(shortDuration * 2);

  // Second pattern: one long beep
  tone(Buzzer, freqHigh, longDuration);
  delay(longDuration * 2);

  // Third pattern: rapid short beeps
  for (int i = 0; i < 5; i++) {
    tone(Buzzer, freqLow, shortDuration);
    delay(shortDuration);
  }
}