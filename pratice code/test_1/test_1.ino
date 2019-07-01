int i = 1;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(100);
  Serial.println("hello world");
  
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(i);
  i = i+1;
  delay(1000);
} 
