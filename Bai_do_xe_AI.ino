#include <Arduino.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <LiquidCrystal_I2C.h>

U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

Servo servoEnter, servoExit;

#define ir_enter 19
#define ir_exit 23
#define ir_car1 12
#define ir_car2 27
#define ir_car3 2
#define ir_car4 15

#define ledRed 32
#define ledYellow 33
#define ledGreen 25

int S1, S2, S3, S4;
int flagEnter = 0, flagExit = 0;
int slot = 0;

String plate = "";
#define MAX_CAR 5
String carList[MAX_CAR];
int carCount = 0;

int findPlate(String plate) {
  for (int i = 0; i < carCount; i++) {
    if (carList[i] == plate) {
      return i;
    }
  }
  return -1;
}

void handleCarEnter(String plate) {
  digitalWrite(ledYellow, HIGH);
  delay(1000);
  digitalWrite(ledYellow, LOW);

  if (slot == 0) {
    digitalWrite(ledRed, HIGH);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("XIN LOI");
    lcd.setCursor(0, 1);
    lcd.print("DA HET CHO DO XE");
    delay(3000);
    lcd.clear();
    digitalWrite(ledRed, LOW);
    return;
  }

  if (findPlate(plate) != -1) {
    Serial.println("Xe da ton tai trong bai");
    u8g2.clearBuffer();
    u8g2.drawStr(30, 30, "ERROR IN!");
    u8g2.sendBuffer();
    delay(3000);
    u8g2.clearBuffer();
    return;
  }

  flagEnter = 1;
  carList[carCount++] = plate;
  digitalWrite(ledGreen, HIGH);
  servoEnter.write(180);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Bien so xe: ");
  lcd.setCursor(0, 1);
  lcd.print(plate);
  delay(2000);
  lcd.clear();
  servoEnter.write(90);
  digitalWrite(ledGreen, LOW);
  flagEnter = 0;
}

void handleCarExit(String plate) {
  int index = findPlate(plate);

  if (index == -1) {
    Serial.println("Khong tim thay bien so xe");
    u8g2.clearBuffer();
    u8g2.drawStr(30, 30, "ERROR OUT!");
    u8g2.sendBuffer();
    delay(3000);
    u8g2.clearBuffer();
    return;
  }

  flagExit = 1;
  for (int i = index; i < carCount - 1; i++) {
    carList[i] = carList[i + 1];
  }
  carCount--;

  digitalWrite(ledYellow, HIGH);
  delay(1000);
  servoExit.write(180);
  delay(2000);
  servoExit.write(90);
  digitalWrite(ledYellow, LOW);
  flagExit = 0;
}

void setup() {
  Serial.begin(115200);

  pinMode(ir_enter, INPUT);
  pinMode(ir_exit, INPUT);
  pinMode(ir_car1, INPUT);
  pinMode(ir_car2, INPUT);
  pinMode(ir_car3, INPUT);
  pinMode(ir_car4, INPUT);

  servoEnter.attach(18);
  servoExit.attach(5);
  servoEnter.write(90);
  servoExit.write(90);

  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledYellow, OUTPUT);
  digitalWrite(ledRed, LOW);
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledYellow, LOW);

  Wire.begin();
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(29, 20, "TRAM DO XE");
  u8g2.drawStr(40, 40, "TU DONG");
  u8g2.sendBuffer();

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("ESP32 READY");
  lcd.setCursor(0, 1);
  lcd.print("Waiting AI...");
  
  delay(3000);
  updateSlots();
}

void loop() {
  updateSlots();

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("BAI DO XE TM");

  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n') {
      plate.trim();

      Serial.print("Nhan bien so: ");
      Serial.println(plate);

      if (digitalRead(ir_enter) == LOW && flagEnter == 0) {
        handleCarEnter(plate);
      }
      else if (digitalRead(ir_exit) == LOW && flagExit == 0) {
        handleCarExit(plate);
      }
      
      plate = "";
    }
    else {
      plate += c;
    }
  }
}

void updateSlots() {
  S1 = !digitalRead(ir_car1);
  S2 = !digitalRead(ir_car2);
  S3 = !digitalRead(ir_car3);
  S4 = !digitalRead(ir_car4);

  slot = 4 - (S1 + S2 + S3 + S4);

  u8g2.firstPage();
  do {
    u8g2.drawStr(20, 25, "S1:");
    u8g2.drawStr(40, 25, S1 ? "X" : ".");
    u8g2.drawStr(80, 25, "S2:");
    u8g2.drawStr(100, 25, S2 ? "X" : ".");
    u8g2.drawStr(20, 40, "S3:");
    u8g2.drawStr(40, 40, S3 ? "X" : ".");
    u8g2.drawStr(80, 40, "S4:");
    u8g2.drawStr(100, 40, S4 ? "X" : ".");
  } while (u8g2.nextPage());
}