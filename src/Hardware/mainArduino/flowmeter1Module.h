int flowPin = 2;    //This is the input pin on the Arduino
double flowRate;    //This is the value we intend to calculate.
volatile double count


void setupFlow(){
  pinMode(flowPin, INPUT);
  attachInterrupt(0, Flow, RISING);
}


