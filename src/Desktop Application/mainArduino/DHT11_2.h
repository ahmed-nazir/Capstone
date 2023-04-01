// === HUMIDITY SENSOR MODULE === //

#include <DHT.h>


DHT DHT11_2(5, DHT11);

struct DHT11_2_SensorValues{
  float A;
};

void setupDHT11_2(char PIN){
  DHT11_2 = DHT(PIN,DHT11);
  DHT11_2.begin();
  
}

DHT11_2_SensorValues readDHT11_2(char PIN){
  DHT11_2_SensorValues values;

  values.A = DHT11_2.readHumidity();
  
  return values;
}