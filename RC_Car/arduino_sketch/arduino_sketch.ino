#include <SoftwareSerial.h>

// --- 핀 설정 ---
SoftwareSerial BTSerial(2, 4); // 블루투스 RX=2, TX=4

int B_IA = 3;  // 왼쪽 모터 A
int B_IB = 5;  // 왼쪽 모터 B
int A_IA = 6;  // 오른쪽 모터 A
int A_IB = 11; // 오른쪽 모터 B

const int FSR_L_PIN = A1; // 왼쪽 FSR 센서
const int FSR_R_PIN = A0; // 오른쪽 FSR 센서

// --- 설정 변수 ---
int speed = 150;              
unsigned long lastLogTime = 0;
const int LOG_INTERVAL = 5;   // 200Hz 샘플링 (5ms)

void setup() {
  Serial.begin(115200); // PC 로깅용 속도
  BTSerial.begin(9600); // 블루투스 조종용 속도
  
  pinMode(A_IA, OUTPUT); pinMode(A_IB, OUTPUT);
  pinMode(B_IA, OUTPUT); pinMode(B_IB, OUTPUT);

  stopCar(); 
  delay(2000); 
  
  // CSV 헤더 출력
  Serial.println("timestamp,fsr_left,fsr_right");
}

void loop() {
  // 1. 블루투스 명령 수신 (조종)
  if (BTSerial.available()) {
    char cmd = BTSerial.read();
    manualControl(cmd);
  }

  // 2. FSR 데이터 전송 (USB 로깅)
  unsigned long currentMillis = millis();
  if (currentMillis - lastLogTime >= LOG_INTERVAL) {
    lastLogTime = currentMillis;
    
    int fsrLeft = analogRead(FSR_L_PIN);
    int fsrRight = analogRead(FSR_R_PIN);
    
    Serial.print(currentMillis);
    Serial.print(","); 
    Serial.print(fsrLeft);
    Serial.print(","); 
    Serial.println(fsrRight);
  }
}

void manualControl(char cmd) {
  if (cmd == 'w') { // 전진
    digitalWrite(B_IA, LOW); analogWrite(B_IB, speed);
    digitalWrite(A_IA, LOW); analogWrite(A_IB, speed);
  } 
  else if (cmd == 's') { // 후진
    analogWrite(B_IA, speed); digitalWrite(B_IB, LOW);
    analogWrite(A_IA, speed); digitalWrite(A_IB, LOW);
  } 
  else if (cmd == 'a') { // 좌회전
    digitalWrite(B_IA, LOW); analogWrite(B_IB, 0);
    digitalWrite(A_IA, LOW); analogWrite(A_IB, speed);
  } 
  else if (cmd == 'd') { // 우회전
    digitalWrite(B_IA, LOW); analogWrite(B_IB, speed);
    digitalWrite(A_IA, LOW); analogWrite(A_IB, 0);
  } 
  else if (cmd == 'x') { // 정지
    stopCar();
  }
}

void stopCar() {
  digitalWrite(A_IA, LOW); digitalWrite(A_IB, LOW);
  digitalWrite(B_IA, LOW); digitalWrite(B_IB, LOW);
}