/*
 * ============================================================================
 * ECOVERSE 360 — Air Quality Monitor Firmware
 * ESP32 + MQ135 (Gas) + PMS5003 (Particulate) + DHT22 (Temp/Humidity)
 * 
 * Measures: AQI, PM2.5, PM10, CO2 (est.), Temperature, Humidity
 * Sends data via MQTT every 60 seconds.
 * ============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ── Configuration ───────────────────────────────────────────────────────

const char* WIFI_SSID      = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD";
const char* MQTT_SERVER     = "YOUR_MQTT_BROKER_IP";
const int   MQTT_PORT       = 1883;
const char* MQTT_USER       = "ecoverse";
const char* MQTT_PASSWORD   = "ecoverse360";
const char* DEVICE_ID       = "AIR-001";
const char* LOCATION        = "Campus Main Gate";

String TOPIC_DATA   = String("ecoverse/sensors/") + DEVICE_ID + "/data";
String TOPIC_STATUS = String("ecoverse/sensors/") + DEVICE_ID + "/status";

// ── Hardware Pins ───────────────────────────────────────────────────────

#define MQ135_PIN       34      // Analog input for MQ135
#define DHT_PIN         4       // DHT22 data pin
#define DHT_TYPE        DHT22
#define PMS_RX          16      // PMS5003 serial RX
#define PMS_TX          17      // PMS5003 serial TX
#define LED_STATUS      2       // Built-in LED

// ── Constants ───────────────────────────────────────────────────────────

#define READING_INTERVAL_MS 60000   // 60 seconds
#define MQ135_R0            76.63   // Sensor resistance in clean air (calibrate!)
#define MQ135_RL            10.0    // Load resistance in kΩ

// ── Objects ─────────────────────────────────────────────────────────────

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);
HardwareSerial pmsSerial(1);  // UART1 for PMS5003

unsigned long lastReadTime = 0;

// PMS5003 data structure
struct PMSData {
    uint16_t pm10_standard;
    uint16_t pm25_standard;
    uint16_t pm100_standard;
    uint16_t pm10_env;
    uint16_t pm25_env;
    uint16_t pm100_env;
};

PMSData pmsData;

// ── Setup ───────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    pmsSerial.begin(9600, SERIAL_8N1, PMS_RX, PMS_TX);
    
    Serial.println("\n=== ECOVERSE 360 — Air Quality Monitor ===");
    Serial.printf("Device: %s | Location: %s\n", DEVICE_ID, LOCATION);

    pinMode(MQ135_PIN, INPUT);
    pinMode(LED_STATUS, OUTPUT);

    dht.begin();
    connectWiFi();
    mqtt.setServer(MQTT_SERVER, MQTT_PORT);
    connectMQTT();

    // Allow sensors to warm up
    Serial.println("Warming up sensors (30s)...");
    delay(30000);
    
    sendStatus("online");
}

// ── Main Loop ───────────────────────────────────────────────────────────

void loop() {
    if (!mqtt.connected()) connectMQTT();
    mqtt.loop();

    if (millis() - lastReadTime >= READING_INTERVAL_MS) {
        lastReadTime = millis();
        
        // Read all sensors
        float temperature = dht.readTemperature();
        float humidity = dht.readHumidity();
        float co2_ppm = readCO2();
        readPMS5003();
        
        // Calculate simple AQI based on PM2.5
        float aqi = calculateAQI(pmsData.pm25_env);

        // Build JSON payload
        StaticJsonDocument<384> doc;
        doc["device_id"] = DEVICE_ID;
        doc["location"] = LOCATION;
        doc["type"] = "air_quality";
        
        JsonObject readings = doc.createNestedObject("readings");
        readings["aqi"] = round(aqi);
        readings["pm25"] = pmsData.pm25_env;
        readings["pm10"] = pmsData.pm100_env;
        readings["co2_ppm"] = round(co2_ppm);
        readings["temperature"] = isnan(temperature) ? -1 : round(temperature * 10) / 10.0;
        readings["humidity"] = isnan(humidity) ? -1 : round(humidity * 10) / 10.0;

        char payload[384];
        serializeJson(doc, payload);

        mqtt.publish(TOPIC_DATA.c_str(), payload, true);

        // Log
        Serial.printf("AQI: %.0f | PM2.5: %d | PM10: %d | CO2: %.0f ppm | "
                      "Temp: %.1f°C | Humidity: %.1f%%\n",
            aqi, pmsData.pm25_env, pmsData.pm100_env, co2_ppm,
            temperature, humidity);

        // Alert for poor air quality
        if (aqi > 150) {
            Serial.println("⚠️  Air quality is UNHEALTHY!");
            digitalWrite(LED_STATUS, HIGH);
        } else {
            digitalWrite(LED_STATUS, LOW);
        }
    }
}

// ── Sensor Reading Functions ────────────────────────────────────────────

float readCO2() {
    /*
     * Estimate CO2 from MQ135 analog reading.
     * Note: MQ135 is not precise for CO2 — use SCD30/SCD40 for production.
     * This gives a rough approximation for demo/prototype.
     */
    int rawValue = analogRead(MQ135_PIN);
    float voltage = rawValue * (3.3 / 4095.0);  // ESP32 12-bit ADC
    float rsRatio = ((3.3 * MQ135_RL) / voltage - MQ135_RL) / MQ135_R0;
    
    // Approximate CO2 from Rs/R0 ratio (from MQ135 datasheet curve)
    float co2 = 116.6020682 * pow(rsRatio, -2.769034857);
    
    if (co2 < 400) co2 = 400;   // Ambient minimum
    if (co2 > 5000) co2 = 5000; // Sensor max
    
    return co2;
}

bool readPMS5003() {
    /*
     * Read PMS5003 particulate matter sensor via serial.
     * Returns true if valid data received.
     */
    uint8_t buffer[32];
    int idx = 0;

    // Wait for start bytes 0x42 0x4D
    unsigned long start = millis();
    while (millis() - start < 1000) {
        if (pmsSerial.available()) {
            uint8_t b = pmsSerial.read();
            if (idx == 0 && b == 0x42) {
                buffer[idx++] = b;
            } else if (idx == 1 && b == 0x4D) {
                buffer[idx++] = b;
            } else if (idx >= 2 && idx < 32) {
                buffer[idx++] = b;
                if (idx == 32) break;
            } else {
                idx = 0;
            }
        }
    }

    if (idx < 32) return false;

    // Parse data (big-endian 16-bit values)
    pmsData.pm10_standard  = (buffer[4]  << 8) | buffer[5];
    pmsData.pm25_standard  = (buffer[6]  << 8) | buffer[7];
    pmsData.pm100_standard = (buffer[8]  << 8) | buffer[9];
    pmsData.pm10_env       = (buffer[10] << 8) | buffer[11];
    pmsData.pm25_env       = (buffer[12] << 8) | buffer[13];
    pmsData.pm100_env      = (buffer[14] << 8) | buffer[15];

    return true;
}

float calculateAQI(uint16_t pm25) {
    /*
     * Simple AQI calculation based on PM2.5 concentration.
     * Uses US EPA breakpoints.
     */
    struct Breakpoint { float cLow, cHigh, iLow, iHigh; };
    Breakpoint bp[] = {
        {0.0,   12.0,  0,   50},
        {12.1,  35.4,  51,  100},
        {35.5,  55.4,  101, 150},
        {55.5,  150.4, 151, 200},
        {150.5, 250.4, 201, 300},
        {250.5, 500.4, 301, 500},
    };

    float c = (float)pm25;
    for (int i = 0; i < 6; i++) {
        if (c >= bp[i].cLow && c <= bp[i].cHigh) {
            return ((bp[i].iHigh - bp[i].iLow) / (bp[i].cHigh - bp[i].cLow))
                   * (c - bp[i].cLow) + bp[i].iLow;
        }
    }
    return 500;  // Beyond scale
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
        Serial.printf("\nConnected! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\nFailed! Restarting...");
        ESP.restart();
    }
}

void connectMQTT() {
    int attempts = 0;
    while (!mqtt.connected() && attempts < 5) {
        Serial.printf("MQTT connecting to %s...", MQTT_SERVER);
        if (mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASSWORD)) {
            Serial.println(" OK!");
        } else {
            Serial.printf(" failed (rc=%d)\n", mqtt.state());
            delay(2000);
            attempts++;
        }
    }
}

void sendStatus(const char* status) {
    StaticJsonDocument<128> doc;
    doc["device_id"] = DEVICE_ID;
    doc["status"] = status;
    doc["type"] = "air_quality";
    doc["uptime_ms"] = millis();
    
    char payload[128];
    serializeJson(doc, payload);
    mqtt.publish(TOPIC_STATUS.c_str(), payload);
}
