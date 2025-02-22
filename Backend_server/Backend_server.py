from flask_cors import CORS
from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)
CORS(app)

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["plant_database"]
plants_collection = db["plants"]

# Friend's Flask Server API URL (Tanish's Server)
FRIEND_SERVER_URL = "http://192.168.0.18:5001/sensor_data"
UPDATE_MOISTURE_URL = "http://192.168.0.18:5001/update_moisture"

# Load the JSON data from the file
with open("plants_data2.json", "r", encoding="utf-8") as file:
    plant_data = json.load(file)

# Function to add dataset to MongoDB
def add_plant_data():
    if plants_collection.count_documents({}) == 0:
        plants_collection.insert_many(plant_data)
        print("🌱 1000 Plant dataset added to MongoDB!")
    else:
        print("✅ Plant dataset already exists in MongoDB.")

# Home Route
@app.route('/')
def home():
    return "Backend Server is Running!", 200

@app.route('/fetch_sensor_data', methods=['GET'])
def fetch_sensor_data():
    # """ Fetch the latest sensor data from friend's server """
    try:
        sensor_response = requests.get(FRIEND_SERVER_URL, timeout=2)
        if sensor_response.status_code == 200:
            return sensor_response.json(), 200
        else:
            return jsonify({"error": "Failed to fetch sensor data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Compare Real-time Sensor Data with MongoDB Dataset
@app.route('/compare_plant', methods=['POST'])
def compare_plant():
    try:
        data = request.json
        print(f"🌱 Received Data: {data}")
        plant_name = data.get("name", "").lower()

        if not plant_name:
            return jsonify({"error": "Plant name is required"}), 400

        # Fetch plant details
        plant = plants_collection.find_one({"name": {"$regex": f"^{plant_name}$", "$options": "i"}})
        if not plant:
            print(f"❌ ERROR: Plant '{plant_name}' not found in MongoDB!")
            return jsonify({"error": "Plant not found"}), 404
        
        print(f"✅ Found Plant in DB: {plant}")
        plant["_id"] = str(plant["_id"])  # Convert ObjectId to string

        # Fetch real-time sensor data
        try:
            sensor_response = requests.get(FRIEND_SERVER_URL, timeout=2)
            if sensor_response.status_code == 200:
                sensor_data = sensor_response.json()
                data_source = "real"
            else:
                raise Exception("Failed to fetch real sensor data")
        except Exception as e:
            print(f"❌ Sensor Fetch Error: {e}")
            sensor_data = {
                "soil_moisture": None,
                "temperature": None,
                "humidity": None,
                "light_intensity": None
            }
            data_source = "dummy"

        # ✅ Ensure None values are replaced with defaults
        soil_moisture = sensor_data.get("soil_moisture")
        temperature = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
        light_intensity = sensor_data.get("light_intensity")

        # ✅ Convert None values to default floats
        if soil_moisture is None:
            soil_moisture = 0.0
        if temperature is None:
            temperature = 0.0
        if humidity is None:
            humidity = 0.0
        if light_intensity is None:
            light_intensity = 0.0

        # Generate care suggestions
        suggestions = []
        pump_status = "OFF"

        if soil_moisture < plant["ideal_moisture"]:
            suggestions.append("Increase watering 🌱💧")
            pump_status = "ON"
        elif soil_moisture > plant["ideal_moisture"]:
            suggestions.append("Reduce watering 🚫💧")
            pump_status = "OFF"

        if temperature < plant["ideal_temperature"]:
            suggestions.append("Increase temperature 🔥")
        elif temperature > plant["ideal_temperature"]:
            suggestions.append("Decrease temperature ❄️")

        if humidity < plant["ideal_humidity"]:
            suggestions.append("Increase humidity 🌫️")
        elif humidity > plant["ideal_humidity"]:
            suggestions.append("Decrease humidity 💨")

        if light_intensity < plant["ideal_light"]:
            suggestions.append("Move plant to more light ☀️")
        elif light_intensity > plant["ideal_light"]:
            suggestions.append("Move plant to shade 🌳")

        # Send updated moisture & pump status to friend's server
        try:
            update_response = requests.post(
                UPDATE_MOISTURE_URL, 
                json={"threshold": plant["ideal_moisture"], "pump_status": pump_status},
                timeout=2
            )
            if update_response.status_code == 200:
                print(f"✅ Pump status updated successfully: {pump_status}")
            else:
                print(f"❌ Failed to update pump status. Response: {update_response.text}")
        except Exception as e:
            print(f"❌ Error sending pump status update: {e}")

        return jsonify({
            "plant": plant,
            "sensor_data": {
                "soil_moisture": soil_moisture,
                "temperature": temperature,
                "humidity": humidity,
                "light_intensity": light_intensity
            },
            "suggestions": suggestions,
            "data_source": data_source,
            "pump_status": pump_status
        }), 200

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    add_plant_data()
    app.run(host='0.0.0.0', port=5002, debug=True)
