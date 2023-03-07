#include <SoftwareSerial.h>
#include <SPI.h>
#include <SD.h>

#include "temperatureModule.h"
#include "humidityModule.h"
#include "accelerometerModule.h"
#include "thermister1Module.h"

File myFile;
SoftwareSerial espSerial(2,3);

const int chipSelect = 10;

int wiredSend = 0;
int wifiSend = 0;
int wiredRead;
int wifiRead;

#define HEADER "AccelerationX1,AccelerationY1,AccelerationZ1,Temperature1"
#define dataString String(X_out) + "," + String(Y_out) + "," + String(Z_out) + "," + String(temperature)



void readData(){
  readAccelerometer();
  readTemp();
  //readHumidity();
  readThermister1();
}

void setup() {
  
  Serial.begin(9600);
  espSerial.begin(9600);
  SD.begin();
  
  setupTemp();
  //setupHumidity();
  setupAccelerometer();
  setupThermister1();

}

void loop() {

  // === Start and Stop Wireless Serial Comm === //
  wifiRead = espSerial.read();
  if(wifiRead == 81){
    wifiSend = 1;
    SD.remove("TestData.csv");
    myFile = SD.open("TestData.csv", FILE_WRITE);
    if (myFile) {
      String Headers = HEADER;
      myFile.println(Headers);
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
    espSerial.print('D');
    espSerial.print(1); 
    espSerial.print(temperature);
    espSerial.print(',');    
    espSerial.print('F');
    espSerial.print(1);
    espSerial.print(R2);
    espSerial.print(',');
    espSerial.print('G');
    espSerial.print(1);
    espSerial.print(tCelsius); 
    //espSerial.print(',');
    //espSerial.print('E');
    //espSerial.print(1); 
    //espSerial.print(humidity);
    espSerial.println(')');

    // === Write Data to SD Card === //
    myFile = SD.open("TestData.csv", FILE_WRITE);
    if (myFile) {
      String dataValues = dataString;
      myFile.println(dataValues);
      myFile.close();
    } 
    
    delay(1100);
    
  }
  
  
  
  // === Start & Stop Wired Serial Comm === //
  wiredRead = Serial.read();
  if(wiredRead == 'G'){
    wiredSend = 1;
    SD.remove("TestData.csv");
    myFile = SD.open("TestData.csv", FILE_WRITE);
    if (myFile) {
      String Headers = HEADER;
      myFile.println(Headers);
      myFile.close();
    }
  }
  else if(wiredRead == 'P'){
    wiredSend =0;
  }
  
  if(wiredSend){
    readData();
  
    // === Send Bytestring to Serial Port === //
    Serial.print('(');
    //Serial.print('A');
    //Serial.print(1);           
    //Serial.print(X_out);
    //Serial.print(',');
    //Serial.print('B');
    //Serial.print(1); 
    //Serial.print(Y_out);
    //Serial.print(',');
    //Serial.print('C');
    //Serial.print(1); 
    //Serial.print(Z_out);
    //Serial.print(',');
    Serial.print('D');
    Serial.print(1); 
    Serial.print(temperature);
    Serial.print(',');
    Serial.print('F');
    Serial.print(1);
    Serial.print(R2);
    Serial.print(',');
    Serial.print('G');
    Serial.print(1);
    Serial.print(tCelsius);        
    //Serial.print(',');
    //Serial.print('E');
    //Serial.print(1); 
    //Serial.print(humidity);
    Serial.println(')');

   // === Write Data to SD Card === //
    myFile = SD.open("TestData.csv", FILE_WRITE);
    if (myFile) {
      String dataValues = dataString;
      myFile.println(dataValues);
      myFile.close();
    } 
    
    delay(1100); //Speed of transmission
  }
}
