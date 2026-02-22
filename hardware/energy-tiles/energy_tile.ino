/*
 * ============================================================================
 * ECOVERSE 360 — Piezoelectric Energy Harvesting Tile
 * ESP8266 + Piezo Sensor + Step Counter + Energy Estimation
 * 
 * Monitors: Footstep impacts, energy generated, step count
 * Sends data via MQTT every 60 seconds.
 * ============================================================================
 */

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ── Configuration ───────────────────────────────────────────────────────

const char* WIFI_SSID      = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD";
const char* MQTT_SERVER     = "YOUR_MQTT_BROKER_IP";
const char* DEVICE_ID       = "TILE-001";
const char* LOCATION        = "Main Corridor A";

String TOPIC_DATA = String("ecoverse/energy/tiles/") + DEVICE_ID;

// ── Hardware Pins ───────────────────────────────────────────────────────

#define PIEZO_PIN           A0      // Piezo analog output
#define LED_STEP            D1      // Blink on step
#define LED_STATUS          D4      // Status LED

// ── Constants ───────────────────────────────────────────────────────────

#define REPORT_INTERVAL_MS      60000   // Report every 60 seconds
#define STEP_THRESHOLD          150     // ADC threshold for a step
#define DEBOUNCE_MS             200     // Debounce between steps
#define ENERGY_PER_STEP_MJ      0.005   // Millijoules per step (typical piezo)
#define SAMPLE_RATE_US          1000    // 1ms sampling

// ── State ───────────────────────────────────────────────────────────────

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

volatile unsigned long stepCount = 0;
volatile unsigned long sessionSteps = 0;
volatile float totalEnergy = 0;        // mJ accumulated
unsigned long lastReportTime = 0;
unsigned long lastStepTime = 0;
unsigned long peakForce = 0;
unsigned long intervalSteps = 0;
float intervalEnergy = 0;

// ── Setup ───────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== ECOVERSE 360 — Energy Tile ===");
    Serial.printf("Device: %s | Location: %s\n", DEVICE_ID, LOCATION);

    pinMode(LED_STEP, OUTPUT);
    pinMode(LED_STATUS, OUTPUT);
    digitalWrite(LED_STEP, LOW);

    connectWiFi();
    mqtt.setServer(MQTT_SERVER, 1883);
    connectMQTT();

    lastReportTime = millis();
}

// ── Main Loop ───────────────────────────────────────────────────────────

void loop() {
    if (!mqtt.connected()) connectMQTT();
    mqtt.loop();

    // --- Continuous piezo sampling ---
    int piezoValue = analogRead(PIEZO_PIN);

    if (piezoValue > STEP_THRESHOLD && (millis() - lastStepTime) > DEBOUNCE_MS) {
        lastStepTime = millis();
        stepCount++;
        sessionSteps++;
        intervalSteps++;

        // Energy estimation based on impact magnitude
        float impactRatio = (float)piezoValue / 1023.0;
        float energy = ENERGY_PER_STEP_MJ * impactRatio * 2.0;  // Scale by impact
        totalEnergy += energy;
        intervalEnergy += energy;

        if ((unsigned long)piezoValue > peakForce) peakForce = piezoValue;

        // Visual feedback
        digitalWrite(LED_STEP, HIGH);
        delay(50);
        digitalWrite(LED_STEP, LOW);
    }

    // --- Periodic MQTT Report ---
    if (millis() - lastReportTime >= REPORT_INTERVAL_MS) {
        publishReport();
        lastReportTime = millis();
    }

    delayMicroseconds(SAMPLE_RATE_US);
}

// ── Reporting ───────────────────────────────────────────────────────────

void publishReport() {
    float stepsPerMinute = intervalSteps;  // Already 1-min interval
    float energyWh = totalEnergy / 3600000.0;  // mJ → Wh
    float intervalEnergyWh = intervalEnergy / 3600000.0;

    StaticJsonDocument<320> doc;
    doc["device_id"] = DEVICE_ID;
    doc["type"] = "energy_tile";
    doc["location"] = LOCATION;

    JsonObject readings = doc.createNestedObject("readings");
    readings["steps_total"] = stepCount;
    readings["steps_interval"] = intervalSteps;
    readings["steps_per_minute"] = stepsPerMinute;
    readings["energy_total_mj"] = round(totalEnergy * 100) / 100.0;
    readings["energy_total_wh"] = round(energyWh * 10000) / 10000.0;
    readings["energy_interval_mj"] = round(intervalEnergy * 100) / 100.0;
    readings["peak_force"] = peakForce;

    // Traffic density classification
    const char* density;
    if (stepsPerMinute > 30) density = "very_high";
    else if (stepsPerMinute > 15) density = "high";
    else if (stepsPerMinute > 5) density = "medium";
    else if (stepsPerMinute > 0) density = "low";
    else density = "none";
    readings["traffic_density"] = density;

    char payload[320];
    serializeJson(doc, payload);
    mqtt.publish(TOPIC_DATA.c_str(), payload, true);

    Serial.printf("Steps: %lu (+%lu) | Energy: %.4f Wh | Traffic: %s | Peak: %lu\n",
        stepCount, intervalSteps, energyWh, density, peakForce);

    // Reset interval counters
    intervalSteps = 0;
    intervalEnergy = 0;
    peakForce = 0;
}

// ── Connection Functions ────────────────────────────────────────────────

void connectWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) { delay(500); }
    Serial.printf("WiFi: %s\n", WiFi.localIP().toString().c_str());
}

void connectMQTT() {
    while (!mqtt.connected()) {
        if (mqtt.connect(DEVICE_ID, "ecoverse", "ecoverse360")) break;
        delay(2000);
    }
}
