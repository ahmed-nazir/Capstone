// === HUMIDITY SENSOR MODULE === //

// - Connect to Arduino Digital Pin 8

#include <DHT.h>

#define DHTPIN 8 
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);


float humidity;


void setupHumidity(){
  dht.begin();
}

void readHumidity(){
  // === Read Humidity Data (DHT11) === //
  humidity = dht.readHumidity();
}