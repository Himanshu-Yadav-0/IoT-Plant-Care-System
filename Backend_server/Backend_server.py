
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
with open("plants_data.json", "r", encoding="utf-8") as file:
    plant_data = json.load(file)

# Function to add dataset to MongoDB
def add_plant_data():
    if plants_collection.count_documents({}) == 0:
        plants_collection.insert_many(plant_data)
        print("\U0001F331 1000 Plant dataset added to MongoDB!")
    else:
        print("\u2705 Plant dataset already exists in MongoDB.")

# Home Route
@app.route('/')
def home():
    return "Backend Server is Running!", 200

@app.route('/fetch_sensor_data', methods=['GET'])
def fetch_sensor_data():
    """ Fetch the latest sensor data from friend's server """
    try:
        sensor_response = requests.get(FRIEND_SERVER_URL, timeout=3)  # Fetch from your friend's Flask server
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
        plant_name = data.get("name", "").lower()

        if not plant_name:
            return jsonify({"error": "Plant name is required"}), 400

        # Fetch plant details
        plant = plants_collection.find_one({"name": {"$regex": f"^{plant_name}$", "$options": "i"}})

        if not plant:
            return jsonify({"error": "Plant not found"}), 404

        plant["_id"] = str(plant["_id"])  # Convert ObjectId to string

        # Fetch real-time sensor data from Tanish's server
        try:
            sensor_response = requests.get(FRIEND_SERVER_URL, timeout=3)
            if sensor_response.status_code == 200:
                sensor_data = sensor_response.json()
                data_source = "real"
            else:
                raise Exception("Failed to fetch real sensor data")
        except:
            sensor_data = {
                "soil_moisture": 40,
                "temperature": 26,
                "humidity": 55,
                "light_intensity": 450000
            }
            data_source = "dummy"

        # Generate care suggestions
        suggestions = []
        pump_status = "OFF"
        if sensor_data["soil_moisture"] < plant["ideal_moisture"]:
            suggestions.append("Increase watering \U0001F331\U0001F4A7")
            pump_status = "ON"
        elif sensor_data["soil_moisture"] > plant["ideal_moisture"]:
            suggestions.append("Reduce watering \U0001F6AB\U0001F4A7")
            pump_status = "OFF"

        if sensor_data["temperature"] < plant["ideal_temperature"]:
            suggestions.append("Increase temperature \U0001F525")
        elif sensor_data["temperature"] > plant["ideal_temperature"]:
            suggestions.append("Decrease temperature \u2744")

        if sensor_data["humidity"] < plant["ideal_humidity"]:
            suggestions.append("Increase humidity \U0001F32B")
        elif sensor_data["humidity"] > plant["ideal_humidity"]:
            suggestions.append("Decrease humidity \U0001F4A8")

        if sensor_data["light_intensity"] < plant["ideal_light"]:
            suggestions.append("Move plant to more light \u2600")
        elif sensor_data["light_intensity"] > plant["ideal_light"]:
            suggestions.append("Move plant to shade \U0001F333")

        # Send updated moisture & pump status to Tanish's server
        requests.post(UPDATE_MOISTURE_URL, json={"soil_moisture": sensor_data["soil_moisture"], "pump_status": pump_status})

        return jsonify({
            "plant": plant,
            "sensor_data": sensor_data,
            "suggestions": suggestions,
            "data_source": data_source,
            "pump_status": pump_status
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    add_plant_data()
    app.run(host='0.0.0.0', port=5002, debug=True)
