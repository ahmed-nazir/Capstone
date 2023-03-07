

int ThermistorPin = 3;
int Vo;
float R1 = 25000;
float logR2, R2, tKelvin, tCelsius, tFahrenheit;
float c1 = 1.466529121e-03, c2 = 1.336132238e-04, c3 = 3.488125576e-07;

void setupThermister1(){
  pinMode(ThermistorPin, INPUT);
}


void readThermister1(){
  Vo = analogRead(ThermistorPin);
  R2 = R1 * (1023.0 / (float)Vo - 1.0); // resistance of the Thermistor
  logR2 = log(R2);
  tKelvin = (1.0 / (c1 + c2 * logR2 + c3 * logR2 * logR2 * logR2));
  tCelsius = tKelvin - 273.15;
  tFahrenheit = (tCelsius * 9.0) / 5.0 + 32.0;
}