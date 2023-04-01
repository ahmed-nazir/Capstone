// === THERMISTER MODULE === //

// Struct Containing the # of Outputs
struct THERMISTER_1_SensorValues{
  float A;

};

void setupTHERMISTER_1(char PIN){  
  pinMode(PIN, INPUT);
}

THERMISTER_1_SensorValues readTHERMISTER_1(char PIN){
  THERMISTER_1_SensorValues values;

  int Vo;
  float R1 = 25000;
  float logR2, R2, tKelvin, tCelsius, tFahrenheit;
  float c1 = 1.466529121e-03, c2 = 1.336132238e-04, c3 = 3.488125576e-07;

  int Vo = analogRead(PIN);
  R2 = R1 * (1023.0 / (float)Vo - 1.0); // resistance of the Thermistor
  logR2 = log(R2);

  tCelsius = tKelvin - 273.15;


  values.A = tCelsius;


  return values;
}