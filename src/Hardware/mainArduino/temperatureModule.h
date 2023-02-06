// === TEMPERATURE SENSOR MODULE === //

// - Connect to Arduino Analong Pin 0

#define PIN 0

float temperature;
int temperaturePin = PIN;

void setupTemp(){

}

void readTemp(){
  // === Read Temperature Data (LM35) === //
  temperature = analogRead(temperaturePin); // read analog volt from sensor and save to variable temp
  temperature = temperature * 0.48828125; // convert the analog volt to its temperature equivalent
}