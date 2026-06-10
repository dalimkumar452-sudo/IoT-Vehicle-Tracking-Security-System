from flask import Flask, render_template, jsonify, request
import paho.mqtt.client as mqtt
import json
import math
import random
import threading
import time

app = Flask(__name__)

# --- MQTT Setup ---
MQTT_BROKER = "broker.emqx.io" 
MQTT_PORT = 8083  
TOPIC_LIVE = "iot/vehicle/live_data"
TOPIC_CMD = "iot/vehicle/command"

# --- Geofence & Base Configuration ---
HOME_LAT = 22.5726
HOME_LNG = 88.3639
GEOFENCE_RADIUS_METERS = 500

# Global shared state
vehicle_data = {
    "lat": 22.5726,
    "lng": 88.3639,
    "speed": 0,
    "engine": "ON",
    "distance": 0,
    "geofence_status": "Inside"
}

mqtt_connected = False
sim_step = 0

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(R * c)

# --- Autonomous Smart Simulation Engine ---
def autonomous_simulation_engine():
    global vehicle_data, sim_step
    print("🤖 Autonomous Smart Simulation Engine Started Running in Background...")
    
    while True:
        # If MQTT is connected and receiving real data, we don't overwrite it
        if not mqtt_connected:
            sim_step += 1
            
            # State 1: Normal Movement inside Geofence (Steps 1-15)
            if sim_step <= 15:
                if vehicle_data["engine"] == "ON":
                    vehicle_data["lat"] += 0.0002
                    vehicle_data["lng"] += 0.0002
                    vehicle_data["speed"] = random.randint(35, 55)
                else:
                    vehicle_data["speed"] = 0

            # State 2: Vehicle Leaves Safe Zone / Outside Geofence (Steps 16-30)
            elif sim_step <= 30:
                if vehicle_data["engine"] == "ON":
                    vehicle_data["lat"] += 0.0003
                    vehicle_data["lng"] += 0.0001
                    vehicle_data["speed"] = random.randint(60, 80)
                else:
                    vehicle_data["speed"] = 0

            # State 3: Vehicle gets Parked & Owner Locks it (Steps 31-40)
            elif sim_step <= 40:
                vehicle_data["speed"] = 0
                # Auto-trigger lock for simulation demonstration if not changed manually
                if sim_step == 31:
                    print("🔒 Simulation: Vehicle parked. Simulating remote LOCK command.")
                    vehicle_data["engine"] = "LOCKED"

            # State 4: Theft Simulation - Unexpected movement while engine is locked (Steps 41+)
            else:
                vehicle_data["lat"] -= 0.0002
                vehicle_data["lng"] += 0.0003
                vehicle_data["speed"] = random.randint(40, 70)

            # Core Logic Calculations
            dist = calculate_distance(HOME_LAT, HOME_LNG, vehicle_data["lat"], vehicle_data["lng"])
            vehicle_data["distance"] = dist
            
            # Evaluate Status
            if vehicle_data["engine"] == "LOCKED" and vehicle_data["speed"] > 0:
                vehicle_data["geofence_status"] = "🚨 THEFT ALERT! Unauthorized Movement!"
            elif dist > GEOFENCE_RADIUS_METERS:
                vehicle_data["geofence_status"] = "⚠️ Outside Geofence!"
            else:
                vehicle_data["geofence_status"] = "Inside Safe Zone"
                
        time.sleep(2) # Update telemetry every 2 seconds

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        print("\n✅ Connected to MQTT Broker via WebSockets!")
        mqtt_connected = True
        client.subscribe(TOPIC_LIVE)
    else:
        print(f"MQTT Connection failed with code {rc}")

def on_message(client, userdata, msg):
    global vehicle_data
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        vehicle_data["lat"] = payload.get("lat", vehicle_data["lat"])
        vehicle_data["lng"] = payload.get("lng", vehicle_data["lng"])
        vehicle_data["speed"] = int(payload.get("speed", 0))
        vehicle_data["engine"] = payload.get("engine", vehicle_data["engine"])
        
        dist = calculate_distance(HOME_LAT, HOME_LNG, vehicle_data["lat"], vehicle_data["lng"])
        vehicle_data["distance"] = dist
        
        if vehicle_data["engine"] == "LOCKED" and vehicle_data["speed"] > 0:
            vehicle_data["geofence_status"] = "🚨 THEFT ALERT! Unauthorized Movement!"
        elif dist > GEOFENCE_RADIUS_METERS:
            vehicle_data["geofence_status"] = "⚠️ Outside Geofence!"
        else:
            vehicle_data["geofence_status"] = "Inside Safe Zone"
    except Exception as e:
        print("Error processing incoming MQTT message:", e)

# Initialize and spin up MQTT Client safely
try:
    client_id = f"flask_hybrid_client_{random.randint(100, 999)}"
    mqtt_client = mqtt.Client(client_id=client_id, transport="websockets")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    print(f"Trying background cloud synchronization with {MQTT_BROKER}...")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 10) # 10 second quick timeout
    mqtt_client.loop_start()
except Exception as e:
    print(f"ℹ️ Cloud Sync Bypass: Operating in local isolated mode due to network restrictions.")

# Start the fallback simulation engine thread automatically
sim_thread = threading.Thread(target=autonomous_simulation_engine, daemon=True)
sim_thread.start()

# --- Flask Server Endpoints ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/telemetry')
def telemetry():
    return jsonify(vehicle_data)

@app.route('/api/command', methods=['POST'])
def command():
    global vehicle_data
    cmd = request.json.get('action')
    if cmd in ['LOCK', 'UNLOCK']:
        # If MQTT works, publish it
        if mqtt_connected:
            mqtt_client.publish(TOPIC_CMD, cmd)
        
        # Immediately reflect change locally so the dashboard responds instantly
        vehicle_data["engine"] = "LOCKED" if cmd == "LOCK" else "ON"
        return jsonify({"status": "success", "command_sent": cmd})
    return jsonify({"status": "failed"}), 400

if __name__ == '__main__':
    print("\n🚀 Launching Pro Vehicle Security Dashboard Server...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)