/*
 * ============================================================================
 * ECOVERSE 360 — Smart Bin Firmware
 * ESP8266/ESP32 + HC-SR04 Ultrasonic + HX711 Load Cell
 * 
 * Measures bin fill level (%) and weight (kg),
 * sends data via MQTT to Ecoverse backend.
 * ============================================================================
 */

#include <ESP8266WiFi.h>        // Use <WiFi.h> for ESP32
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ── Configuration ───────────────────────────────────────────────────────

// WiFi
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD  = "YOUR_WIFI_PASSWORD";

// MQTT
const char* MQTT_SERVER    = "YOUR_MQTT_BROKER_IP";
const int   MQTT_PORT      = 1883;
const char* MQTT_USER      = "ecoverse";
const char* MQTT_PASSWORD  = "ecoverse360";

// Device Identity
const char* DEVICE_ID      = "BIN-001";
const char* BIN_CATEGORY   = "plastic";      // plastic, organic, metal, paper, glass
const char* LOCATION       = "Main Building Entrance";

// MQTT Topics
String TOPIC_DATA   = String("ecoverse/bins/") + DEVICE_ID + "/update";
String TOPIC_STATUS = String("ecoverse/sensors/") + DEVICE_ID + "/status";

// ── Hardware Pins ───────────────────────────────────────────────────────

// Ultrasonic Sensor (HC-SR04)
#define TRIG_PIN        D1      // GPIO5
#define ECHO_PIN        D2      // GPIO4

// Load Cell (HX711)
#define HX711_DOUT      D5      // GPIO14
#define HX711_SCK       D6      // GPIO12

// LED Indicators
#define LED_GREEN       D3      // GPIO0  — bin OK
#define LED_RED         D7      // GPIO13 — bin full

// ── Constants ───────────────────────────────────────────────────────────

#define BIN_HEIGHT_CM       60.0    // Total bin height in cm
#define BIN_EMPTY_DIST_CM   58.0    // Distance reading when bin is empty
#define ALERT_THRESHOLD     80.0    // % fill level to trigger alert
#define READING_INTERVAL_MS 30000   // Send data every 30 seconds
#define CALIBRATION_FACTOR  2280.0  // HX711 calibration (adjust per setup)

// ── Objects ─────────────────────────────────────────────────────────────

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

unsigned long lastReadTime = 0;
float fillLevel = 0;
float weightKg = 0;
bool isFull = false;

// ── HX711 Simple Implementation ────────────────────────────────────────

long hx711Read() {
    // Simplified HX711 reading — use HX711 library in production
    long value = 0;
    digitalWrite(HX711_SCK, LOW);
    while (digitalRead(HX711_DOUT)) {}  // Wait for ready

    for (int i = 0; i < 24; i++) {
        digitalWrite(HX711_SCK, HIGH);
        value = (value << 1) | digitalRead(HX711_DOUT);
        digitalWrite(HX711_SCK, LOW);
    }

    // Set gain to 128
    digitalWrite(HX711_SCK, HIGH);
    digitalWrite(HX711_SCK, LOW);

    if (value & 0x800000) value |= 0xFF000000;  // Sign extend
    return value;
}

// ── Setup ───────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== ECOVERSE 360 — Smart Bin ===");
    Serial.printf("Device: %s | Category: %s\n", DEVICE_ID, BIN_CATEGORY);

    // Pin modes
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(HX711_DOUT, INPUT);
    pinMode(HX711_SCK, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_RED, OUTPUT);

    // Initial LED state
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);

    // Connect WiFi
    connectWiFi();

    // Configure MQTT
    mqtt.setServer(MQTT_SERVER, MQTT_PORT);
    connectMQTT();

    // Send initial status
    sendStatus("online");
}

// ── Main Loop ───────────────────────────────────────────────────────────

void loop() {
    // Maintain connections
    if (!mqtt.connected()) connectMQTT();
    mqtt.loop();

    // Read sensors at interval
    if (millis() - lastReadTime >= READING_INTERVAL_MS) {
        lastReadTime = millis();

        // Read fill level (ultrasonic)
        fillLevel = readFillLevel();

        // Read weight (load cell)
        weightKg = readWeight();

        // Check if full
        bool wasFull = isFull;
        isFull = (fillLevel >= ALERT_THRESHOLD);

        // Update LEDs
        updateLEDs();

        // Send data
        sendBinData();

        // Log
        Serial.printf("[%s] Level: %.1f%% | Weight: %.2f kg | Full: %s\n",
            DEVICE_ID, fillLevel, weightKg, isFull ? "YES" : "no");

        // Alert if just became full
        if (isFull && !wasFull) {
            Serial.println("⚠️  BIN IS FULL — Alert sent!");
        }
    }
}

// ── Sensor Reading Functions ────────────────────────────────────────────

float readFillLevel() {
    // Trigger ultrasonic pulse
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Read echo
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // timeout 30ms
    if (duration == 0) return fillLevel;  // keep last value on timeout

    float distanceCm = (duration * 0.0343) / 2.0;

    // Calculate fill percentage
    // When bin is empty, distance is max (BIN_EMPTY_DIST_CM)
    // When bin is full, distance is small (~5 cm)
    float level = ((BIN_EMPTY_DIST_CM - distanceCm) / BIN_EMPTY_DIST_CM) * 100.0;

    // Clamp to 0-100
    if (level < 0) level = 0;
    if (level > 100) level = 100;

    return level;
}

float readWeight() {
    // Read from HX711 load cell
    long raw = hx711Read();
    float weight = raw / CALIBRATION_FACTOR;
    if (weight < 0) weight = 0;
    return weight;
}

// ── Communication Functions ─────────────────────────────────────────────

void sendBinData() {
    StaticJsonDocument<256> doc;
    doc["device_id"] = DEVICE_ID;
    doc["category"] = BIN_CATEGORY;
    doc["level"] = round(fillLevel * 10) / 10.0;  // 1 decimal
    doc["weight"] = round(weightKg * 100) / 100.0;
    doc["is_full"] = isFull;
    doc["location"] = LOCATION;
    doc["battery"] = 100;  // placeholder — add battery monitoring

    char payload[256];
    serializeJson(doc, payload);

    mqtt.publish(TOPIC_DATA.c_str(), payload, true);
}

void sendStatus(const char* status) {
    StaticJsonDocument<128> doc;
    doc["device_id"] = DEVICE_ID;
    doc["status"] = status;
    doc["uptime_ms"] = millis();

    char payload[128];
    serializeJson(doc, payload);

    mqtt.publish(TOPIC_STATUS.c_str(), payload);
}

// ── Connection Functions ────────────────────────────────────────────────

void connectWiFi() {
    Serial.printf("Connecting to WiFi: %s", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\nWiFi connected! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\nWiFi connection failed! Restarting...");
        ESP.restart();
    }
}

void connectMQTT() {
    int attempts = 0;
    while (!mqtt.connected() && attempts < 5) {
        Serial.printf("Connecting MQTT to %s...", MQTT_SERVER);
        if (mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASSWORD)) {
            Serial.println(" connected!");
        } else {
            Serial.printf(" failed (rc=%d). Retry in 2s...\n", mqtt.state());
            delay(2000);
            attempts++;
        }
    }
}

void updateLEDs() {
    if (isFull) {
        digitalWrite(LED_GREEN, LOW);
        digitalWrite(LED_RED, HIGH);
    } else if (fillLevel > 60) {
        // Blink green for medium level
        digitalWrite(LED_GREEN, (millis() / 500) % 2);
        digitalWrite(LED_RED, LOW);
    } else {
        digitalWrite(LED_GREEN, HIGH);
        digitalWrite(LED_RED, LOW);
    }
}
