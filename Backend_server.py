from flask_cors import CORS
from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
import json


app = Flask(__name__)
CORS(app)


# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"  # Change this if needed
client = MongoClient(MONGO_URI)
db = client["plant_database"]
plants_collection = db["plants"]

# Friend's Flask Server API URL
FRIEND_SERVER_URL = "http://<friend's-ip>:5001/sensor_data"  # Replace <friend's-ip> with actual IP

# Load the JSON data from the file
with open("plants_data.json", "r", encoding="utf-8") as file:
    plant_data = json.load(file)
# Sample dataset (replace with actual dataset)
sample_plants = plant_data

# Function to add dataset to MongoDB
def add_plant_data():
    if plants_collection.count_documents({}) == 0:  # If the collection is empty
        plants_collection.insert_many(sample_plants)
        print("🌱 1000 Plant dataset added to MongoDB!")
    else:
        print("✅ Plant dataset already exists in MongoDB.")
# Home Route
@app.route('/')
def home():
    return "Backend Server is Running!", 200


# API Compare Real time sensor data to the Dataset in mongodb
@app.route('/compare_plant', methods=['POST'])
def compare_plant():
    try:
        data = request.json
        plant_name = data.get("name", "").lower()

        if not plant_name:
            return jsonify({"error": "Plant name is required"}), 400

        # Fetch plant details using case-insensitive regex search
        plant = plants_collection.find_one({"name": {"$regex": f"^{plant_name}$", "$options": "i"}})

        if not plant:
            return jsonify({"error": "Plant not found"}), 404

        # Convert ObjectId to string to avoid serialization errors
        plant["_id"] = str(plant["_id"])

        # Try fetching real-time sensor data
        try:
            sensor_response = requests.get(FRIEND_SERVER_URL, timeout=3)  # 3-sec timeout
            if sensor_response.status_code == 200:
                sensor_data = sensor_response.json()
            else:
                raise Exception("Failed to fetch real sensor data")
        except:
            # Dummy sensor data for testing
            sensor_data = {
                "soil_moisture": 40,   # Example moisture %
                "temperature": 26,      # Example temperature in °C
                "humidity": 55,         # Example humidity %
                "light_intensity": 450000  # Example light intensity in lux
            }

        # Generate care suggestions
        suggestions = []
        if sensor_data["soil_moisture"] < plant["ideal_moisture"]:
            suggestions.append("Increase watering 🌱💧")
        elif sensor_data["soil_moisture"] > plant["ideal_moisture"]:
            suggestions.append("Reduce watering 🚫💧")

        if sensor_data["temperature"] < plant["ideal_temperature"]:
            suggestions.append("Increase temperature 🔥")
        elif sensor_data["temperature"] > plant["ideal_temperature"]:
            suggestions.append("Decrease temperature ❄️")

        if sensor_data["humidity"] < plant["ideal_humidity"]:
            suggestions.append("Increase humidity 🌫️")
        elif sensor_data["humidity"] > plant["ideal_humidity"]:
            suggestions.append("Decrease humidity 💨")

        if sensor_data["light_intensity"] < plant["ideal_light"]:
            suggestions.append("Move plant to more light ☀️")
        elif sensor_data["light_intensity"] > plant["ideal_light"]:
            suggestions.append("Move plant to shade 🌳")

        return jsonify({
            "plant": plant,
            "sensor_data": sensor_data,
            "suggestions": suggestions,
            "data_source": "real" if "real" in locals() else "dummy"  # Indicates if data is real or dummy
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# API to send updated soil moisture data to Friend's Flask Server
@app.route('/update_moisture', methods=['POST'])
def update_moisture():
    try:
        data = request.json
        soil_moisture = data.get("soil_moisture")

        if soil_moisture is None:
            return jsonify({"error": "Soil moisture data required"}), 400

        # Send data to friend's Flask API
        response = requests.post(FRIEND_SERVER_URL, json={"soil_moisture": soil_moisture})
        
        if response.status_code == 200:
            return jsonify({"message": "Soil moisture updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update soil moisture"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    add_plant_data()  # Add the dataset to MongoDB if it's empty
    app.run(host='0.0.0.0', port=5002, debug=True)  # Runs on port 5002
