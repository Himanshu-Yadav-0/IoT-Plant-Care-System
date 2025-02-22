from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app)

# Store latest sensor data
latest_sensor_data = {}
moisture_threshold = 50.0  # Default threshold
pump_status = "OFF"  # Default pump status

# Home Route
@app.route('/')
def home():
    return "ESP8266 Flask Server is Running!", 200

# ✅ API to Get Current Moisture Threshold
@app.route('/moisture_threshold', methods=['GET'])
def get_moisture_threshold():
    global moisture_threshold
    return jsonify({"moisture_threshold": moisture_threshold}), 200  # ✅ Fixed syntax

# ✅ API to Receive Sensor Data from ESP8266
@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    global latest_sensor_data, pump_status
    try:
        latest_sensor_data = request.json
        soil_moisture = latest_sensor_data.get("soil_moisture")

        # Update pump status based on moisture level
        if soil_moisture is not None:
            pump_status = "ON" if soil_moisture < moisture_threshold else "OFF"
        
        print("📩 Received Sensor Data:", latest_sensor_data)
        return jsonify({"message": "Sensor data received", "pump_status": pump_status}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ API to Get Latest Sensor Data
@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    return jsonify(latest_sensor_data or {
        "soil_moisture": None, "temperature": None,
        "humidity": None, "light_intensity": None,
        "pump_status": "UNKNOWN"
    }), 200

# ✅ Updated API to `/update_moisture`
@app.route('/update_moisture', methods=['GET', 'POST'])
def handle_update_moisture():
    global moisture_threshold

    if request.method == 'GET':
        return jsonify({"threshold": moisture_threshold}), 200

    elif request.method == 'POST':
        data = request.json
        if "threshold" in data:
            moisture_threshold = float(data["threshold"])
            return jsonify({"message": "Threshold updated", "threshold": moisture_threshold}), 200
        else:
            return jsonify({"error": "Missing threshold value"}), 400

# ✅ API to Get Pump Status
@app.route('/pump_status', methods=['GET'])
def get_pump_status():
    return jsonify({"pump_status": pump_status}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
