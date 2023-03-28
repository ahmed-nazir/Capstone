#include <SoftwareSerial.h>
#include <SPI.h>
#include <SD.h>
#include "ADXL345_1.h"
#include "LM35_1.h"

File myFile;
SoftwareSerial espSerial(2,3);

const int chipSelect = 10;

int wiredSend = 0;
int wifiSend = 0;
int wiredRead;
int wifiRead;

float AccelerationX1;
float AccelerationY1;
float AccelerationZ1;
float Temperature1;

void readData(){
  ADXL345_1_SensorValues ADXL345_1_Values = readADXL345_1();
  LM35_1_SensorValues LM35_1_Values = readLM35_1();
  AccelerationX1 = ADXL345_1_Values.A;
  AccelerationY1 = ADXL345_1_Values.B;
  AccelerationZ1 = ADXL345_1_Values.C;
  Temperature1 = LM35_1_Values.A;
}
void setup() {
  Serial.begin(9600);
  espSerial.begin(9600);
  SD.begin();

  setupADXL345_1();
  setupLM35_1();
}

void loop() {
  // === Start and Stop Wireless Serial Comm === //
  wifiRead = espSerial.read();
  if(wifiRead == 81){
    wifiSend = 1;
    SD.remove("TestData.txt");
    myFile = SD.open("TestData.txt", FILE_WRITE);
    if (myFile) {
      myFile.close();
     }
  }
  if(wifiRead == 87){
    wifiSend = 0;
  }

  if(wifiSend){
    readData();

    // === Send Bytestring to Serial Port === //
    espSerial.print('(');
    espSerial.print('A');
    espSerial.print(1);
    espSerial.print(AccelerationX1);
    espSerial.print(',');
    espSerial.print('B');
    espSerial.print(1);
    espSerial.print(AccelerationY1);
    espSerial.print(',');
    espSerial.print('C');
    espSerial.print(1);
    espSerial.print(AccelerationZ1);
    espSerial.print(',');
    espSerial.print('D');
    espSerial.print(1);
    espSerial.print(Temperature1);
    espSerial.println(')');

    // === Write Data to SD Card === //
    myFile = SD.open("TestData.txt", FILE_WRITE);
    if (myFile) {
      myFile.print('(');
      myFile.print('A');
      myFile.print(1);
      myFile.print(AccelerationX1);
      myFile.print(',');
      myFile.print('B');
      myFile.print(1);
      myFile.print(AccelerationY1);
      myFile.print(',');
      myFile.print('C');
      myFile.print(1);
      myFile.print(AccelerationZ1);
      myFile.print(',');
      myFile.print('D');
      myFile.print(1);
      myFile.print(Temperature1);
      myFile.println(')');
      myFile.close();
    }
    delay(1100);
  }


  // === Start and Stop Wired Serial Comm === //
  wiredRead = Serial.read();
  if(wiredRead == 'G'){
    wiredSend = 1;
    SD.remove("TestData.txt");
    myFile = SD.open("TestData.txt", FILE_WRITE);
    if (myFile) {
      myFile.close();
     }
  }
  if(wiredRead == 'P'){
    wiredSend = 0;
  }
  if(wiredRead =='R'){
    myFile = SD.open("TestData.txt");
    if (myFile){
      while (myFile.available()){
        Serial.write(myFile.read());
      }
    myFile.close();
    }
  }

  if(wiredSend){
    readData();

    // === Send Bytestring to Serial Port === //
    Serial.print('(');
    Serial.print('A');
    Serial.print(1);
    Serial.print(AccelerationX1);
    Serial.print(',');
    Serial.print('B');
    Serial.print(1);
    Serial.print(AccelerationY1);
    Serial.print(',');
    Serial.print('C');
    Serial.print(1);
    Serial.print(AccelerationZ1);
    Serial.print(',');
    Serial.print('D');
    Serial.print(1);
    Serial.print(Temperature1);
    Serial.println(')');

    // === Write Data to SD Card === //
    myFile = SD.open("TestData.txt", FILE_WRITE);
    if (myFile) {
      myFile.print('(');
      myFile.print('A');
      myFile.print(1);
      myFile.print(AccelerationX1);
      myFile.print(',');
      myFile.print('B');
      myFile.print(1);
      myFile.print(AccelerationY1);
      myFile.print(',');
      myFile.print('C');
      myFile.print(1);
      myFile.print(AccelerationZ1);
      myFile.print(',');
      myFile.print('D');
      myFile.print(1);
      myFile.print(Temperature1);
      myFile.println(')');
      myFile.close();
    }
    delay(1100);
  }
}
