// === TRANSDUCER MODULE === //

// Struct Containing the # of Outputs
struct TRANSDUCER_1_SensorValues{
  float A;
  float B;
};

void setupTRANSDUCER_1(char PIN){  
  pinMode(PIN, INPUT);
}

TRANSDUCER_1_SensorValues readTRANSDUCER_1(char PIN){
  TRANSDUCER_1_SensorValues values;

  float sensorValue;
  float output;
  const float NullVal = 0.1;
  const float FullVal = 0.9;
  const float FSS = FullVal-NullVal;
  sensorValue = analogRead(PIN);
  output = 100*(sensorValue-1023*NullVal)/(FSS*1023);


  values.A = sensorValue;
  values.B = output;

  return values;
}

