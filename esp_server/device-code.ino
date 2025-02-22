#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>

// WiFi Credentials
const char* ssid = "Hood";
const char* password = "TUMCHUTIYAHO69";

// Flask Server IP
const char* serverUrl = "http://192.168.0.18:5001/sensor_data";  
const char* thresholdUrl = "http://192.168.0.18:5001/moisture_threshold";  

// Sensor Pins
#define DHTPIN D4        
#define DHTTYPE DHT11    
#define SOIL_PIN A0      
#define RELAY_PIN D5     

// I2C Pins for BH1750
#define SDA_PIN D2       
#define SCL_PIN D1       

// Sensor Objects
DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;

WiFiClient client;
HTTPClient http;

// Moisture Threshold
float moistureThreshold = 50.0;

// Timing Variables
unsigned long lastDHTReadTime = 0;
unsigned long lastServerSendTime = 0;

void setup() {
    Serial.begin(115200);
    
    dht.begin();
    delay(2000);  

    Wire.begin(SDA_PIN, SCL_PIN);
    lightMeter.begin();

    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH);  // Initially OFF

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    int retry = 0;
    while (WiFi.status() != WL_CONNECTED && retry < 20) {
        delay(1000);
        Serial.print(".");
        retry++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ Connected to WiFi!");
    } else {
        Serial.println("\n❌ Failed to connect! Restarting...");
        ESP.restart();
    }s
}

void loop() {
    unsigned long currentMillis = millis();

    // Read sensors every 2 seconds
    if (currentMillis - lastDHTReadTime >= 2000) {
        lastDHTReadTime = currentMillis;
        readAndProcessSensors();
    }

    // Fetch threshold & Send data every 5 seconds
    if (currentMillis - lastServerSendTime >= 2000) {
        lastServerSendTime = currentMillis;
        
        getMoistureThreshold();  
        sendDataToServer();
    }
}

void readAndProcessSensors() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float lightIntensity = lightMeter.readLightLevel();
    int rawSoilMoisture = analogRead(SOIL_PIN);

    float soilMoisturePercent = 100.0 - ((rawSoilMoisture / 1023.0) * 100.0);

    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("❌ Failed to read from DHT11 sensor!");
        return;
    }

    Serial.printf("🌱 Soil Moisture: %.2f%%\n", soilMoisturePercent);
    Serial.printf("🌡 Temperature: %.2f°C\n", temperature);
    Serial.printf("💧 Humidity: %.2f%%\n", humidity);
    Serial.printf("☀ Light Intensity: %.2f lux\n", lightIntensity);

    // Pump Control Based on Updated Threshold
    if (soilMoisturePercent < moistureThreshold) {
        digitalWrite(RELAY_PIN, LOW);  
        Serial.println("🚰 Pump ON!");
    } else {
        digitalWrite(RELAY_PIN, HIGH);  
        Serial.println("❌ Pump OFF!");
    }
}

void getMoistureThreshold() {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    http.begin(client, thresholdUrl);  
    int httpResponseCode = http.GET();

    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.println("📥 Threshold Response: " + response);

        StaticJsonDocument<128> jsonDoc;
        DeserializationError error = deserializeJson(jsonDoc, response);
        if (!error && jsonDoc.containsKey("moisture_threshold")) {  // ✅ Corrected JSON key
            moistureThreshold = jsonDoc["moisture_threshold"].as<float>();
            Serial.printf("🔄 Updated Moisture Threshold: %.2f\n", moistureThreshold);
        } else {
            Serial.println("❌ Error parsing JSON response!");
        }
    } else {
        Serial.printf("❌ Failed to get threshold! HTTP Code: %d\n", httpResponseCode);
    }
    
    http.end();
}

void sendDataToServer() {
    if (WiFi.status() != WL_CONNECTED) return;

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float lightIntensity = lightMeter.readLightLevel();
    int rawSoilMoisture = analogRead(SOIL_PIN);

    float soilMoisturePercent = 100.0 - ((rawSoilMoisture / 1023.0) * 100.0);

    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("❌ Skipping data send due to invalid DHT11 readings!");
        return;
    }

    // JSON Payload
    StaticJsonDocument<256> jsonDoc;
    jsonDoc["soil_moisture"] = soilMoisturePercent;
    jsonDoc["temperature"] = temperature;
    jsonDoc["humidity"] = humidity;
    jsonDoc["light_intensity"] = lightIntensity;
    jsonDoc["pump_status"] = (soilMoisturePercent < moistureThreshold) ? "ON" : "OFF";

    String jsonString;
    serializeJson(jsonDoc, jsonString);

    // Send Data to Flask Server
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(jsonString);

    if (httpResponseCode == 200) {
        Serial.println("✅ Data sent successfully!");

        String response = http.getString();
        Serial.println("📩 Server Response: " + response);

        // ✅ Update Pump Status Based on Server Response
        StaticJsonDocument<128> responseJson;
        DeserializationError error = deserializeJson(responseJson, response);
        if (!error && responseJson.containsKey("pump_status")) {
            String pumpStatus = responseJson["pump_status"].as<String>();
            if (pumpStatus == "ON") {
                digitalWrite(RELAY_PIN, LOW);  // ✅ Ensure pump control
                Serial.println("🚰 Pump Turned ON by Server!");
            } else {
                digitalWrite(RELAY_PIN, HIGH);
                Serial.println("❌ Pump Turned OFF by Server!");
            }
        }
    } else {
        Serial.printf("❌ Error sending data! HTTP Code: %d\n", httpResponseCode);
    }

    http.end();
}
