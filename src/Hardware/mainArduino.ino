float temp;
int tempPin = 0;
int a = 0;

int startState = 0;
int stopState = 0;
int incomingByte; 

void setup() {
   Serial.begin(9600);
}

void loop() {
  if(Serial.available()>0){
    incomingByte = Serial.read();
  }

  if(incomingByte == 'G'){
    a = 1;
  }
  else if(incomingByte == 'S'){
    a =0;
  }
  
  if(a==1){
   temp = analogRead(tempPin);
   // read analog volt from sensor and save to variable temp
   temp = temp * 0.48828125;
   // convert the analog volt to its temperature equivalent
   Serial.print(temp); // display temperature value
   Serial.println();
   delay(1000); // update sensor reading each one second
  }
  
  
  /*temp = analogRead(tempPin);
   // read analog volt from sensor and save to variable temp
   temp = temp * 0.48828125;
   // convert the analog volt to its temperature equivalent
   Serial.print(temp); // display temperature value
   Serial.println();
   delay(250); // update sensor reading each one second*/
}
