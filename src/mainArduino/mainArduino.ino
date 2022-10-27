float temp;
int tempPin = 0;
const int startButton = 4;
const int stopButton = 2;
int a  = 0;

int startState = 0;
int stopState = 0;

void setup() {
   Serial.begin(9600);
   pinMode(startButton, INPUT);
   pinMode(stopButton, INPUT);
}

void loop() {
  startState = digitalRead(startButton);
  stopState = digitalRead(stopButton);

  if (startState == HIGH){
    a = 1;
  }
  if(stopState == HIGH){
    a = 0;
  }

  if(a == 1){
   temp = analogRead(tempPin);
   // read analog volt from sensor and save to variable temp
   temp = temp * 0.48828125;
   // convert the analog volt to its temperature equivalent
   Serial.print(temp); // display temperature value
   Serial.println();
   delay(250); // update sensor reading each one second
  }
  
}
