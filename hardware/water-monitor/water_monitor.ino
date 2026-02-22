/*
 * ============================================================================
 * ECOVERSE 360 — Water Quality Monitor Firmware
 * ESP32 + TDS Sensor + pH Sensor + DS18B20 Temperature
 * 
 * Measures: TDS (ppm), pH, Water Temperature
 * Sends data via MQTT every 2 minutes.
 * ============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ── Configuration ───────────────────────────────────────────────────────

const char* WIFI_SSID      = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD";
const char* MQTT_SERVER     = "YOUR_MQTT_BROKER_IP";
const int   MQTT_PORT       = 1883;
const char* DEVICE_ID       = "WATER-001";
const char* LOCATION        = "Campus Water Tank";

String TOPIC_DATA = String("ecoverse/sensors/") + DEVICE_ID + "/data";

// ── Hardware Pins ───────────────────────────────────────────────────────

#define TDS_PIN         34      // TDS sensor analog input
#define PH_PIN          35      // pH sensor analog input
#define TEMP_PIN        4       // DS18B20 data pin
#define LED_STATUS      2

// ── Constants ───────────────────────────────────────────────────────────

#define READING_INTERVAL_MS 120000  // 2 minutes
#define VREF                3.3
#define ADC_RESOLUTION      4096.0
#define PH_OFFSET           0.0     // Calibration offset

// ── Objects ─────────────────────────────────────────────────────────────

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

unsigned long lastReadTime = 0;

// ── Setup ───────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== ECOVERSE 360 — Water Quality Monitor ===");
    
    pinMode(TDS_PIN, INPUT);
    pinMode(PH_PIN, INPUT);
    pinMode(LED_STATUS, OUTPUT);
    
    tempSensor.begin();
    
    connectWiFi();
    mqtt.setServer(MQTT_SERVER, MQTT_PORT);
    connectMQTT();
}

// ── Main Loop ───────────────────────────────────────────────────────────

void loop() {
    if (!mqtt.connected()) connectMQTT();
    mqtt.loop();

    if (millis() - lastReadTime >= READING_INTERVAL_MS) {
        lastReadTime = millis();

        // Read temperature first (needed for TDS compensation)
        tempSensor.requestTemperatures();
        float waterTemp = tempSensor.getTempCByIndex(0);
        if (waterTemp < -50) waterTemp = 25.0;  // fallback

        // Read TDS
        float tdsValue = readTDS(waterTemp);

        // Read pH
        float phValue = readPH();

        // Determine water quality
        String quality = assessQuality(tdsValue, phValue);

        // Build payload
        StaticJsonDocument<256> doc;
        doc["device_id"] = DEVICE_ID;
        doc["location"] = LOCATION;
        doc["type"] = "water_quality";
        
        JsonObject readings = doc.createNestedObject("readings");
        readings["tds_ppm"] = round(tdsValue);
        readings["ph"] = round(phValue * 100) / 100.0;
        readings["temperature"] = round(waterTemp * 10) / 10.0;
        readings["quality"] = quality;

        char payload[256];
        serializeJson(doc, payload);
        mqtt.publish(TOPIC_DATA.c_str(), payload, true);

        Serial.printf("TDS: %.0f ppm | pH: %.2f | Temp: %.1f°C | Quality: %s\n",
            tdsValue, phValue, waterTemp, quality.c_str());
    }
}

// ── Sensor Functions ────────────────────────────────────────────────────

float readTDS(float temperature) {
    /*
     * Read TDS with temperature compensation.
     * TDS = Total Dissolved Solids (ppm)
     * Good drinking water: 50-300 ppm
     */
    // Average multiple readings for stability
    long sum = 0;
    for (int i = 0; i < 30; i++) {
        sum += analogRead(TDS_PIN);
        delay(10);
    }
    float avgVoltage = (sum / 30.0) * VREF / ADC_RESOLUTION;

    // Temperature compensation coefficient
    float compensationCoeff = 1.0 + 0.02 * (temperature - 25.0);
    float compensatedVoltage = avgVoltage / compensationCoeff;

    // Convert voltage to TDS (ppm)
    float tds = (133.42 * compensatedVoltage * compensatedVoltage * compensatedVoltage
                - 255.86 * compensatedVoltage * compensatedVoltage
                + 857.39 * compensatedVoltage) * 0.5;

    if (tds < 0) tds = 0;
    return tds;
}

float readPH() {
    /*
     * Read pH sensor.
     * pH 7 = neutral, <7 = acidic, >7 = basic
     * Safe drinking water: 6.5-8.5
     */
    long sum = 0;
    for (int i = 0; i < 20; i++) {
        sum += analogRead(PH_PIN);
        delay(10);
    }
    float avgVoltage = (sum / 20.0) * VREF / ADC_RESOLUTION;

    // Convert voltage to pH
    // Calibration: pH = 7 at ~2.5V, slope ~-5.7 pH/V
    float ph = 7.0 + ((2.5 - avgVoltage) * 5.7) + PH_OFFSET;

    if (ph < 0) ph = 0;
    if (ph > 14) ph = 14;
    return ph;
}

String assessQuality(float tds, float ph) {
    if (tds < 50 && ph >= 6.5 && ph <= 8.5) return "Excellent";
    if (tds < 300 && ph >= 6.5 && ph <= 8.5) return "Good";
    if (tds < 600 && ph >= 6.0 && ph <= 9.0) return "Acceptable";
    if (tds < 1000) return "Poor";
    return "Unsafe";
}

// ── Connection Functions ────────────────────────────────────────────────

void connectWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) { delay(500); }
    Serial.printf("WiFi connected: %s\n", WiFi.localIP().toString().c_str());
}

void connectMQTT() {
    while (!mqtt.connected()) {
        if (mqtt.connect(DEVICE_ID, "ecoverse", "ecoverse360")) {
            Serial.println("MQTT connected");
        } else {
            delay(2000);
        }
    }
}
