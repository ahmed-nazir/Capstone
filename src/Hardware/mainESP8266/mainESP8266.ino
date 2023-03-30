#include <ESP8266WiFi.h>

// ============================================================= 
// Set AP SSID & Password == //
const char *ssid = "Formulate";
const char *password = "capstone";

// == Set Port Number == //
int port = 8080;
// =============================================================

WiFiServer server(port);

void setup() 
{
  Serial.begin(9600);
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  digitalWrite(D1, HIGH);
  
  WiFi.mode(WIFI_STA);
  WiFi.softAP(ssid, password);

  Serial.print("Connected to ");
  Serial.println(ssid);

  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP()); 
   
  server.begin();
}


void loop() 
{
  // == Turn on LED when device is connected == //
  int conn = WiFi.softAPgetStationNum();
  if(conn == 1){
    //digitalWrite(D1, HIGH);
  }
  else if(conn == 0){
    //digitalWrite(D1, LOW);
  }


  // == Communicate with Arduino == //
  WiFiClient client = server.available();
  if (client) {
    if(client.connected())
    {
      Serial.println("Client Connected");
      digitalWrite(D2, HIGH);
      
    }
    
    while(client.connected()){  

      // == Send Data from Network to Arduino == //
      while(client.available()>0){
        Serial.write(client.read()); 
      }
  
      // == Send Data to Network from Arduino == //
      while(Serial.available()>0){
        client.print(Serial.readString());
      }
    }
    
    client.stop();
    Serial.println("Client disconnected");
    digitalWrite(D2, LOW);
       
  }
}
