
#include <Wire.h>  // Wire library - used for I2C communication

int ADXL345 = 0x53; // The ADXL345 sensor I2C address

float X_out, Y_out, Z_out, temperature;  // Outputs

int temperaturePin = 0;
int start = 0;
int incomingByte;

void setup() {
  Serial.begin(9600); // Initiate serial communication for printing the results on the Serial monitor
  Wire.begin(); // Initiate the Wire library
  // Set ADXL345 in measuring mode
  Wire.beginTransmission(ADXL345); // Start communicating with the device 
  Wire.write(0x2D); // Access/ talk to POWER_CTL Register - 0x2D
  // Enable measurement
  Wire.write(8); // (8dec -> 0000 1000 binary) Bit D3 High for measuring enable 
  Wire.endTransmission();
}

void loop() {
  // === Start & Stop Serial Comm === //
  if(Serial.available()>0){
    incomingByte = Serial.read();
  }
  if(incomingByte == 'G'){
    start = 1;
  }
  else if(incomingByte == 'S'){
    start =0;
  }

  if(start ==1){
    // === Read Acceleromter Data === //
    Wire.beginTransmission(ADXL345);
    Wire.write(0x32); // Start with register 0x32 (ACCEL_XOUT_H)
    Wire.endTransmission(false);
    Wire.requestFrom(ADXL345, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
    X_out = ( Wire.read()| Wire.read() << 8); // X-axis value
    X_out = X_out/256; //For a range of +-2g, we need to divide the raw values by 256, according to the datasheet
    Y_out = ( Wire.read()| Wire.read() << 8); // Y-axis value
    Y_out = Y_out/256;
    Z_out = ( Wire.read()| Wire.read() << 8); // Z-axis value
    Z_out = Z_out/256;
  
    // === Read Temperature Data === //
    temperature = analogRead(temperaturePin); // read analog volt from sensor and save to variable temp
    temperature = temperature * 0.48828125; // convert the analog volt to its temperature equivalent
  
    // === Send Bytestring to Serial Port === //
    Serial.print('B');
    Serial.print(X_out);
    Serial.print('S');
    Serial.print(Y_out);
    Serial.print('S');
    Serial.print(Z_out);
    Serial.print('S');
    Serial.print(temperature);
    Serial.print('E');
    Serial.println();// display temperature value
  
    delay(1100); //Speed of transmission
  }
  
}
