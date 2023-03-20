// === HUMIDITY SENSOR MODULE === //

#include <DHT.h>
 

DHT DHT11_1(5, DHT11);

struct DHT11_1_SensorValues{
  float A;
};

void setupDHT11_1(char PIN){
  DHT11_1 = DHT(PIN,DHT11);
  DHT11_1.begin();
  
}

DHT11_1_SensorValues readDHT11_1(char PIN){
  DHT11_1_SensorValues values;

  values.A = DHT11_1.readHumidity();
  
  return values;
}