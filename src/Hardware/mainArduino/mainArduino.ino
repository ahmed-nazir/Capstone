#include <SoftwareSerial.h>
#include <Wire.h>
#include <DHT.h>
#include <SPI.h>
#include <SD.h>

File myFile;

SoftwareSerial espSerial(2,3);

#define DHTPIN 8 
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int chipSelect = 10;

int ADXL345 = 0x53;

float X_out, Y_out, Z_out, temperature, humidity;
int temperaturePin = 0;

int wiredSend = 0;
int wifiSend = 0;
int wiredRead;
int wifiRead;


void setup() {
  
  Serial.begin(9600);
  espSerial.begin(9600);
  dht.begin();
  SD.begin();

  
  Wire.begin(); // Initiate the Wire library
  // Set ADXL345 in measuring mode
  Wire.beginTransmission(ADXL345); // Start communicating with the device 
  Wire.write(0x2D); // Access/ talk to POWER_CTL Register - 0x2D
  // Enable measurement
  Wire.write(8); // (8dec -> 0000 1000 binary) Bit D3 High for measuring enable 
  Wire.endTransmission();

  myFile = SD.open("TestData.csv", FILE_WRITE);
  if (myFile) {
    String Headers = "X,Y,Z,Temperature,Humidity"; 
    myFile.println(Headers);
    myFile.close();
  } 
}

void loop() {

  // === Start and Stop Wireless Serial Comm === //
  wifiRead = espSerial.read();
  if(wifiRead == 81){
    wifiSend = 1;
  }
  if(wifiRead == 87){
    wifiSend = 0;
  }
  
  if(wifiSend){
    // === Read Acceleromter Data (ADXL345) === //
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

    // === Read Temperature Data (LM35) === //
    temperature = analogRead(temperaturePin); // read analog volt from sensor and save to variable temp
    temperature = temperature * 0.48828125; // convert the analog volt to its temperature equivalent

    // === Read Humidity Data (DHT11) === //
    humidity = dht.readHumidity();

    // === Send Bytestring to Serial Port === //
    espSerial.print('B');
    espSerial.print(X_out);
    espSerial.print('S');
    espSerial.print(Y_out);
    espSerial.print('S');
    espSerial.print(Z_out);
    espSerial.print('S');
    espSerial.print(temperature);
    espSerial.print('S');
    espSerial.print(humidity);
    espSerial.println('E');

    // === Write Data to SD Card === //
    myFile = SD.open("TestData.csv", FILE_WRITE);
    if (myFile) {
      String dataValues = String(X_out) + "," + String(Y_out) + "," + String(Z_out) + "," + String(temperature) + "," + String(humidity);
      myFile.println(dataValues);
      myFile.close();
    } 
    
    delay(1100);
    
  }
  
  
  
  // === Start & Stop Wired Serial Comm === //
  wiredRead = Serial.read();
  if(wiredRead == 'G'){
    wiredSend = 1;
  }
  else if(wiredRead == 'P'){
    wiredSend =0;
  }
  
  if(wiredSend){
    // === Read Acceleromter Data (ADXL345) === //
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
  
    // === Read Temperature Data (LM35) === //
    temperature = analogRead(temperaturePin); // read analog volt from sensor and save to variable temp
    temperature = temperature * 0.48828125; // convert the analog volt to its temperature equivalent

    // === Read Humidity Data (DHT11) === //
    float humidity = dht.readHumidity();
  
    // === Send Bytestring to Serial Port === //
    Serial.print('B');
    Serial.print(X_out);
    Serial.print('S');
    Serial.print(Y_out);
    Serial.print('S');
    Serial.print(Z_out);
    Serial.print('S');
    Serial.print(temperature);
    Serial.print('S');
    Serial.print(humidity);
    Serial.println('E');
  
    delay(1100); //Speed of transmission
  }
}
