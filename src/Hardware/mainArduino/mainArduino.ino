#include <SoftwareSerial.h>
#include <SPI.h>
#include <SD.h>

#include "temperatureModule.h"
#include "humidityModule.h"
#include "accelerometerModule.h"

File myFile;
SoftwareSerial espSerial(2,3);

const int chipSelect = 10;

int wiredSend = 0;
int wifiSend = 0;
int wiredRead;
int wifiRead;


void setup() {
  
  Serial.begin(9600);
  espSerial.begin(9600);
  SD.begin();
  
  setupTemp();
  setupHumidity();
  setupAccelerometer();

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

    readAccelerometer();
    readTemp();
    readHumidity();
   

    // === Send Bytestring to Serial Port === //
    espSerial.print('(');
    espSerial.print('A');
    espSerial.print(0);           
    espSerial.print(X_out);
    espSerial.print(',');
    espSerial.print('B');
    espSerial.print(0); 
    espSerial.print(Y_out);
    espSerial.print(',');
    espSerial.print('C');
    espSerial.print(0); 
    espSerial.print(Z_out);
    espSerial.print(',');
    espSerial.print('D');
    espSerial.print(0); 
    espSerial.print(temperature);
    espSerial.print(',');
    espSerial.print('E');
    espSerial.print(0); 
    espSerial.print(humidity);
    espSerial.println(')');

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
    readAccelerometer();
    readTemp();
    readHumidity();
  
    // === Send Bytestring to Serial Port === //
    Serial.print('A');
    Serial.print('(');
    Serial.print(0);           
    Serial.print(X_out);
    Serial.print(',');
    Serial.print('B');
    Serial.print(0); 
    Serial.print(Y_out);
    Serial.print(',');
    Serial.print('C');
    Serial.print(0); 
    Serial.print(Z_out);
    Serial.print(',');
    Serial.print('D');
    Serial.print(0); 
    Serial.print(temperature);
    Serial.print(',');
    Serial.print('E');
    Serial.print(0); 
    Serial.print(humidity);
    Serial.println(')');
  
    delay(1100); //Speed of transmission
  }
}
