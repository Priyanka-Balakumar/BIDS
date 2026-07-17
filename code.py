// Portable Border Intrusion Detection System (BIDS) Prototype

// V8: Power Management (Deep Sleep) Removed for continuous operation.

// GSM Module Removed. Alerts are now WiFi/Blynk only.

// Includes DHT11 (Temp/Humidity) and MQ135 (Air Quality) environmental sensors.

// Target Microcontroller: ESP32





// ----------------------

// Blynk Configuration (MUST BE BEFORE #includes)

// ----------------------

#define BLYNK_TEMPLATE_ID "xxxxx"
#define BLYNK_TEMPLATE_NAME "Border Security Monitor"
#define BLYNK_AUTH_TOKEN "xxxxxx"





// ----------------------

// Libraries

// ----------------------

#include <WiFi.h>

#include <BlynkSimpleEsp32.h>

#include "time.h"

#include <DHT.h> // Library for DHT sensor



// Your WiFi credentials

char ssid[] = "xxx";

char pass[] = "xxxxx";



// ----------------------

// Time & Location Configuration

// ----------------------

const char* ntpServer = "pool.ntp.org";

const long gmtOffset_sec = 19800; // India Standard Time (UTC +5:30)

const int daylightOffset_sec = 0; // No daylight saving

const char* location = "Bengaluru, India";



// ----------------------

// Blynk Virtual Pins

// ----------------------

#define V_TERMINAL        V0

#define V_PIR_STATUS      V1

#define V_VIB_STATUS      V2

#define V_SOUND_LEVEL     V3

#define V_SYSTEM_STATUS   V4

#define V_INTRUSION_TABLE V5

#define V_TEMPERATURE     V6

#define V_HUMIDITY        V7

#define V_AIR_QUALITY     V8



// ----------------------

// Pin Definitions

// ----------------------

const int pirPin = 13;

const int vibPin = 12;

const int soundPin = 34;

const int buzzerPin = 27;

const int ledPin = 26;



#define DHTPIN 14

#define DHTTYPE DHT11

const int mq135AnalogPin = 35;

const int mq135DigitalPin = 15; // Digital pin is read but not used for wakeup



// ----------------------

// Configuration

// ----------------------

const int soundThreshold = 400;

const int airQualityThreshold = 700;

const unsigned long alertDuration = 5000;

const unsigned long resetDelay = 3000;

const unsigned long debounceDelay = 5000; // Increased debounce for continuous mode



// ----------------------

// Global Variables & Objects

// ----------------------

DHT dht(DHTPIN, DHTTYPE);

BlynkTimer timer;



unsigned long lastTriggerTime = 0;

int eventCount = 0;

bool currentlyAlerting = false;

unsigned long alertStartTime = 0;



// ----------------------

// Setup Function (Runs once)

// ----------------------

void setup() {

    Serial.begin(115200);

    Serial.println("\n--------------------");

    Serial.println("BIDS Initializing...");



    pinMode(pirPin, INPUT);

    pinMode(vibPin, INPUT);

    pinMode(mq135DigitalPin, INPUT);

    pinMode(buzzerPin, OUTPUT);

    pinMode(ledPin, OUTPUT);

    digitalWrite(ledPin, LOW);

    dht.begin();

   

    connectToNetwork();

   

    // Setup a timer to send sensor data to Blynk every 2 seconds

    timer.setInterval(2000L, sendSensorData);

   

    Blynk.virtualWrite(V_TERMINAL, "System Initialized and Online.\n");

    Blynk.virtualWrite(V_SYSTEM_STATUS, 1); // Armed

}



// ----------------------

// Main Loop (Runs continuously)

// ----------------------

void loop() {

    Blynk.run();

    timer.run();



    // Handle alert state timeout

    if (currentlyAlerting && (millis() - alertStartTime >= alertDuration)) {

        endAlert();

    }

   

    // Only check for new events if not currently alerting

    if (!currentlyAlerting) {

        checkIntrusion();

        checkEnvironmentalHazard();

    }

}



// ----------------------

// Core Logic Functions

// ----------------------

void checkIntrusion() {

    // Check for trigger only if debounce time has passed

    if (millis() - lastTriggerTime < debounceDelay) {

        return;

    }



    int pirState = digitalRead(pirPin);



    if (pirState == HIGH) {

        Serial.println("PIR Triggered. Checking secondary sensors...");

       

        int vibState = digitalRead(vibPin);

        int soundValue = analogRead(soundPin);

        bool vibrationDetected = (vibState == HIGH);

        bool soundDetected = (soundValue > soundThreshold);



        if (vibrationDetected || soundDetected) {

            String eventReason = vibrationDetected ? "Motion+Vibration" : "Motion+Sound";

            String currentTime = getFormattedTime();



            triggerAlert("INTRUSION: " + eventReason, true);

            Blynk.logEvent("intrusion_alert", "Intrusion Detected: " + eventReason);

            logEventToBlynk(currentTime, eventReason);

        } else {

            Serial.println("Motion detected, but no secondary confirmation. False Positive.");

        }

       

        lastTriggerTime = millis(); // Reset debounce timer after any PIR trigger

    }

}



void checkEnvironmentalHazard() {

    // Check for trigger only if debounce time has passed

    if (millis() - lastTriggerTime < debounceDelay) {

        return;

    }



    int airQualityValue = analogRead(mq135AnalogPin);



    if (airQualityValue > airQualityThreshold) {

        Serial.println("High air quality value detected.");

        String currentTime = getFormattedTime();

       

        triggerAlert("HAZARD: Poor Air Quality", false);

        Blynk.logEvent("hazard_alert", "Poor air quality detected!");

        logEventToBlynk(currentTime, "Hazard: Air Quality");

       

        lastTriggerTime = millis(); // Reset debounce timer

    }

}



void connectToNetwork() {

    Serial.println("Connecting to WiFi and Blynk...");

    WiFi.begin(ssid, pass);

    int retries = 20;

    while (WiFi.status() != WL_CONNECTED && retries > 0) {

        delay(500); Serial.print("."); retries--;

    }



    if (WiFi.status() == WL_CONNECTED) {

        Serial.println("\nWiFi Connected.");

        configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

        Blynk.config(BLYNK_AUTH_TOKEN);

        if (!Blynk.connect()) Serial.println("Failed to connect to Blynk.");

        else Serial.println("Blynk Connected.");

    } else {

        Serial.println("\nFailed to connect to WiFi.");

    }

}



// ----------------------

// Helper & Blynk Functions

// ----------------------

String getFormattedTime() {

  struct tm timeinfo;

  if(!getLocalTime(&timeinfo)){ return "No Time Sync"; }

  char timeStringBuff[50];

  strftime(timeStringBuff, sizeof(timeStringBuff), "%d-%m-%Y %H:%M:%S", &timeinfo);

  return String(timeStringBuff);

}



void sendSensorData() {

    Blynk.virtualWrite(V_PIR_STATUS, digitalRead(pirPin) ? 255 : 0);

    Blynk.virtualWrite(V_VIB_STATUS, digitalRead(vibPin) ? 255 : 0);

    Blynk.virtualWrite(V_SOUND_LEVEL, analogRead(soundPin));

    Blynk.virtualWrite(V_TEMPERATURE, dht.readTemperature());

    Blynk.virtualWrite(V_HUMIDITY, dht.readHumidity());

    Blynk.virtualWrite(V_AIR_QUALITY, analogRead(mq135AnalogPin));

}



void logEventToBlynk(String timestamp, String reason) {

    eventCount++;

    Blynk.virtualWrite(V_INTRUSION_TABLE, "\nlocation", eventCount,"\t" ,timestamp, "\t",reason);

}



void triggerAlert(String message, bool isIntrusion) {

    Serial.println("**********************************");

    Serial.println(message);

    Serial.println("**********************************");

   

    currentlyAlerting = true;

    alertStartTime = millis();



    Blynk.virtualWrite(V_TERMINAL, "******************\n" + message + "\n******************\n");

    Blynk.virtualWrite(V_SYSTEM_STATUS, 0);

   

    digitalWrite(ledPin, HIGH);



    if (isIntrusion) {

        tone(buzzerPin, 1500);

    } else {

        // Since loop is non-blocking, we can't use a for-loop with delay here.

        // A simple continuous tone will be used for hazard in this mode.

        tone(buzzerPin, 2500, alertDuration);

    }

}

void endAlert() {

    Serial.println("Alert Duration ended. Resetting system.");

    Blynk.virtualWrite(V_TERMINAL, "Alert ended. Re-arming system.\n");

    currentlyAlerting = false;

    noTone(buzzerPin);

    digitalWrite(ledPin, LOW);

    Blynk.virtualWrite(V_SYSTEM_STATUS, 1);

    delay(resetDelay); // Short delay before re-arming to prevent instant re-trigger

    lastTriggerTime = millis(); // Reset debounce timer after alert

}
