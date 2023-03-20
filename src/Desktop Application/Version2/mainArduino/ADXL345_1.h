// === ACCELEROMETER MODULE === //
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();


struct ADXL345_1_SensorValues{
  float A;
  float B;
  float C;
};

void setupADXL345_1(){
  accel.begin();
}

ADXL345_1_SensorValues readADXL345_1() {
  ADXL345_1_SensorValues values;

  sensors_event_t event; 
  accel.getEvent(&event);
  values.A = event.acceleration.x;
  values.B = event.acceleration.y;
  values.C = event.acceleration.z;
  
  return values;
}