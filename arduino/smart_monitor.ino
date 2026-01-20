#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"
#include <ArduinoJson.h> // Make sure user installs ArduinoJson library

// DHT11
#define DHTPIN   2
#define DHTTYPE  DHT11
DHT dht(DHTPIN, DHTTYPE);

// MQ3 (analog out)
const int mq3Pin = A0;

// LCD I2C (16x2)
LiquidCrystal_I2C lcd(0x27, 16, 2);   

// Thresholds (Can be adjusted)
int   gasThreshold   = 350;      
float tempMaxFresh   = 30.0;     
float humMaxFresh    = 75.0;     

unsigned long lastUpdate = 0;
const long interval = 2000; // Update every 2 seconds

void setup() {
  pinMode(mq3Pin, INPUT);
  
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(" FOOD MONITOR ");
  delay(1000);

  dht.begin();
  Serial.begin(9600);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - lastUpdate >= interval) {
    lastUpdate = currentMillis;

    int   gasValue = analogRead(mq3Pin);
    float h        = dht.readHumidity();
    float t        = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println(F("{\"error\":\"DHT Sensor Failed\"}"));
      return;
    }

    bool spoiled = (gasValue > gasThreshold || t > tempMaxFresh || h > humMaxFresh);
    const char* status = spoiled ? "SPOILED" : "FRESH";

    // Create JSON for Serial
    // Manual JSON construction to avoid dependency if possible, but ArduinoJson is better.
    // Simpler string formatting for lightweight usage:
    Serial.print("{");
    Serial.print("\"gas\":"); Serial.print(gasValue); Serial.print(",");
    Serial.print("\"temp\":"); Serial.print(t); Serial.print(",");
    Serial.print("\"hum\":"); Serial.print(h); Serial.print(",");
    Serial.print("\"status\":\""); Serial.print(status); Serial.print("\"");
    Serial.println("}");

    // Refresh LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("G:"); lcd.print(gasValue);
    lcd.print(" T:"); lcd.print(t, 1);
    
    lcd.setCursor(0, 1);
    lcd.print("H:"); lcd.print(h, 0);
    lcd.print("% ");
    lcd.print(status);
  }
}
