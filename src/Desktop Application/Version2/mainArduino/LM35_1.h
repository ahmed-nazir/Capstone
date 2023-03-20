// === TEMPERATURE SENSOR MODULE === //

struct LM35_1_SensorValues{
  float A;
};

void setupLM35_1(char PIN){  
  
}

LM35_1_SensorValues readLM35_1(char PIN){
  LM35_1_SensorValues values;

  values.A = analogRead(PIN);
  values.A = values.A * 0.48828125;

  return values;
}