🚗 Enterprise IoT Vehicle Tracking & Theft Prevention System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask)
![ESP32](https://img.shields.io/badge/ESP32-Hardware-red?style=for-the-badge&logo=espressif)
![MQTT](https://img.shields.io/badge/MQTT-IoT%20Protocol-660066?style=for-the-badge&logo=mqtt)

An industry-grade IoT solution designed for real-time vehicle telematics, route tracking, and remote theft prevention. This system features a hybrid architecture combining **ESP32 hardware integration** and an **Autonomous Smart Simulation Engine** for testing behind restrictive firewalls.

## ✨ Core Features
* 📍 **Real-Time GPS Telemetry:** Tracks dynamic coordinates, speed, and distance traveled.
* 🛡️ **Smart Geofencing:** Auto-calculates boundaries and alerts if the vehicle leaves a 500m safe zone.
* 🚨 **Theft Detection & Alerts:** Triggers a critical UI pulse alert if unauthorized movement is detected while the engine is locked.
* 🔒 **Remote Command Center:** Instantly cut off or restore vehicle ignition over the cloud via MQTT.
* 🗺️ **Dynamic Route Trail:** Draws a real-time path history (trail) on a highly detailed Leaflet map.
* 🤖 **Autonomous Simulation Fallback:** Built-in background thread that automatically simulates realistic vehicle movement, parking, and theft scenarios if physical sensors or cloud connections are unavailable.

## 🛠️ Technology Stack
* **Hardware / Firmware:** ESP32, NEO-6M GPS Module, 5V Relay, C++ (Arduino IDE)
* **Backend:** Python, Flask, Paho-MQTT
* **Frontend:** HTML5, CSS3 (Enterprise Dark Theme), JavaScript, Leaflet.js, OpenStreetMap
* **Cloud / Communication:** EMQX Public Broker, WebSockets, MQTT Protocol

## 📁 Folder Structure

```text
IoT-Vehicle-Tracking-System/
│
├── arduino_code/
│   └── vehicle_tracker.ino         # ESP32 C++ Firmware
│
├── dashboard/
│   ├── app.py                      # Flask Server & Simulation Engine
│   ├── requirements.txt            # Python Dependencies
│   └── templates/
│       └── index.html              # Frontend UI Dashboard
│
├── images/                         # Project Screenshots
├── .gitignore                      # Git ignore rules
└── README.md                       # Project Documentation
🚀 How to Run the Dashboard Locally
1. Clone the repository

Bash
git clone https://github.com/dalimkumar452-sudo/IoT-Vehicle-Tracking-Security-System.git

cd IoT-Vehicle-Tracking-Security-System/dashboard
2. Set up a virtual environment (Recommended)

Bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
3. Install Dependencies

Bash
pip install -r requirements.txt
4. Start the Server

Bash
python app.py
The server will launch the Autonomous Simulation Engine if MQTT ports are blocked by your ISP, ensuring the dashboard works perfectly out of the box.

5. Access the Dashboard
Open your browser and navigate to: http://127.0.0.1:5000

📸 Dashboard Preview
💡 Future Scope
Integration with AWS IoT Core for enterprise-level security.

Adding a Firebase backend to store permanent trip history.

Telegram Bot integration for instant mobile push notifications.