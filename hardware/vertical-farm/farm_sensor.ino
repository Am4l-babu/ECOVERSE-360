/*
 * ============================================================================
 * ECOVERSE 360 — Vertical Farm Sensor Node
 * ESP32 + Soil Moisture + DHT22 + BH1750 Light + Soil pH
 * 
 * Monitors: Soil moisture, temperature, humidity, light, pH
 * Sends data via MQTT every 5 minutes.
 * ============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <BH1750.h>

// ── Configuration ───────────────────────────────────────────────────────

const char* WIFI_SSID      = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD";
const char* MQTT_SERVER     = "YOUR_MQTT_BROKER_IP";
const char* DEVICE_ID       = "FARM-001";
const char* PLOT_NAME       = "Microgreens Bed A";

String TOPIC_DATA = String("ecoverse/farm/") + DEVICE_ID + "/data";

// ── Hardware Pins ───────────────────────────────────────────────────────

#define SOIL_MOISTURE_PIN   34
#define SOIL_PH_PIN         35
#define DHT_PIN             4
#define DHT_TYPE            DHT22
#define PUMP_RELAY_PIN      25      // Water pump relay
#define LED_STATUS          2

// I2C for BH1750: SDA=21, SCL=22 (ESP32 default)

// ── Constants ───────────────────────────────────────────────────────────

#define READING_INTERVAL_MS     300000  // 5 minutes
#define MOISTURE_DRY            3500    // ADC value when dry
#define MOISTURE_WET            1500    // ADC value when wet
#define MOISTURE_THRESHOLD      30.0    // Auto-water below this %
#define PUMP_DURATION_MS        5000    // Water for 5 seconds

// ── Objects ─────────────────────────────────────────────────────────────

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);
BH1750 lightMeter;

unsigned long lastReadTime = 0;
bool pumpActive = false;

// ── Setup ───────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== ECOVERSE 360 — Vertical Farm Node ===");
    Serial.printf("Device: %s | Plot: %s\n", DEVICE_ID, PLOT_NAME);

    pinMode(SOIL_MOISTURE_PIN, INPUT);
    pinMode(SOIL_PH_PIN, INPUT);
    pinMode(PUMP_RELAY_PIN, OUTPUT);
    pinMode(LED_STATUS, OUTPUT);
    digitalWrite(PUMP_RELAY_PIN, LOW);  // Pump off

    dht.begin();
    Wire.begin();
    lightMeter.begin();

    connectWiFi();
    mqtt.setServer(MQTT_SERVER, 1883);
    connectMQTT();
}

// ── Main Loop ───────────────────────────────────────────────────────────

void loop() {
    if (!mqtt.connected()) connectMQTT();
    mqtt.loop();

    if (millis() - lastReadTime >= READING_INTERVAL_MS) {
        lastReadTime = millis();

        // Read all sensors
        float soilMoisture = readSoilMoisture();
        float airTemp = dht.readTemperature();
        float humidity = dht.readHumidity();
        float lightLux = lightMeter.readLightLevel();
        float soilPH = readSoilPH();

        // Calculate health score (0-100)
        float health = calculateHealthScore(soilMoisture, airTemp, humidity, lightLux, soilPH);

        // Auto-irrigation
        if (soilMoisture < MOISTURE_THRESHOLD && !pumpActive) {
            activatePump();
        }

        // Build payload
        StaticJsonDocument<384> doc;
        doc["device_id"] = DEVICE_ID;
        doc["plot"] = PLOT_NAME;
        doc["type"] = "vertical_farm";

        JsonObject readings = doc.createNestedObject("readings");
        readings["soil_moisture"] = round(soilMoisture * 10) / 10.0;
        readings["air_temp"] = isnan(airTemp) ? -1 : round(airTemp * 10) / 10.0;
        readings["humidity"] = isnan(humidity) ? -1 : round(humidity * 10) / 10.0;
        readings["light_lux"] = round(lightLux);
        readings["soil_ph"] = round(soilPH * 100) / 100.0;
        readings["health_score"] = round(health * 10) / 10.0;
        readings["pump_active"] = pumpActive;

        char payload[384];
        serializeJson(doc, payload);
        mqtt.publish(TOPIC_DATA.c_str(), payload, true);

        Serial.printf("Moisture: %.1f%% | Temp: %.1f°C | Humidity: %.1f%% | "
                      "Light: %.0f lux | pH: %.2f | Health: %.1f\n",
            soilMoisture, airTemp, humidity, lightLux, soilPH, health);
    }
}

// ── Sensor Functions ────────────────────────────────────────────────────

float readSoilMoisture() {
    long sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += analogRead(SOIL_MOISTURE_PIN);
        delay(10);
    }
    float avg = sum / 10.0;

    // Map to percentage (wet = 100%, dry = 0%)
    float moisture = map(avg, MOISTURE_DRY, MOISTURE_WET, 0, 100);
    if (moisture < 0) moisture = 0;
    if (moisture > 100) moisture = 100;
    return moisture;
}

float readSoilPH() {
    long sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += analogRead(SOIL_PH_PIN);
        delay(10);
    }
    float voltage = (sum / 10.0) * 3.3 / 4096.0;
    float ph = 7.0 + ((2.5 - voltage) * 5.7);
    if (ph < 0) ph = 0;
    if (ph > 14) ph = 14;
    return ph;
}

float calculateHealthScore(float moisture, float temp, float humidity, float light, float ph) {
    float score = 0;

    // Moisture (30-70% ideal)
    if (moisture >= 30 && moisture <= 70) score += 25;
    else if (moisture >= 20 && moisture <= 80) score += 15;
    else score += 5;

    // Temperature (20-30°C ideal for most crops)
    if (!isnan(temp)) {
        if (temp >= 20 && temp <= 30) score += 25;
        else if (temp >= 15 && temp <= 35) score += 15;
        else score += 5;
    }

    // Light (ideal varies, 5000-30000 lux for most)
    if (light >= 5000 && light <= 30000) score += 25;
    else if (light >= 2000 && light <= 50000) score += 15;
    else score += 5;

    // pH (6.0-7.5 ideal for most veggies)
    if (ph >= 6.0 && ph <= 7.5) score += 25;
    else if (ph >= 5.5 && ph <= 8.0) score += 15;
    else score += 5;

    return score;
}

void activatePump() {
    Serial.println("💧 Auto-irrigation activated!");
    pumpActive = true;
    digitalWrite(PUMP_RELAY_PIN, HIGH);
    delay(PUMP_DURATION_MS);
    digitalWrite(PUMP_RELAY_PIN, LOW);
    pumpActive = false;
    Serial.println("💧 Pump stopped.");
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
