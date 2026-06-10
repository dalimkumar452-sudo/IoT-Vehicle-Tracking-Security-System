#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <TinyGPSPlus.h>

// --- WiFi & MQTT Configuration ---
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "broker.hivemq.com"; // Public Auto-Broker
const int mqtt_port = 1883;

// --- Topics ---
const char* topic_publish = "iot/vehicle/live_data";
const char* topic_subscribe = "iot/vehicle/command";

// --- Pins ---
#define RELAY_PIN 25
#define GPS_RX 16
#define GPS_TX 17

WiFiClient espClient;
PubSubClient client(espClient);
TinyGPSPlus gps;
HardwareSerial gpsSerial(2);

bool engine_status = true; // true = ON, false = OFF (Locked)

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Command Received: " + message);

  if (message == "LOCK") {
    digitalWrite(RELAY_PIN, HIGH); // Assuming HIGH turns off engine
    engine_status = false;
  } else if (message == "UNLOCK") {
    digitalWrite(RELAY_PIN, LOW);
    engine_status = true;
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    String clientId = "ESP32_Vehicle_" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected!");
      client.subscribe(topic_subscribe);
    } else {
      delay(5000); // Auto-retry after 5 seconds
    }
  }
}

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Default Unlocked

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Reading GPS Data
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Publish Data every 3 seconds
  static unsigned long lastMsg = 0;
  if (millis() - lastMsg > 3000) {
    lastMsg = millis();

    StaticJsonDocument<200> doc;
    
    if (gps.location.isValid()) {
      doc["lat"] = gps.location.lat();
      doc["lng"] = gps.location.lng();
      doc["speed"] = gps.speed.kmph();
    } else {
      // DUMMY DATA for immediate testing (if real GPS is not locked)
      doc["lat"] = 22.5726 + (random(-100, 100) / 100000.0);
      doc["lng"] = 88.3639 + (random(-100, 100) / 100000.0);
      doc["speed"] = random(20, 60);
    }
    
    doc["engine"] = engine_status ? "ON" : "LOCKED";

    char jsonString[200];
    serializeJson(doc, jsonString);
    client.publish(topic_publish, jsonString);
    Serial.println("Published: " + String(jsonString));
  }
}