# Smart Plant Monitoring & Care System

## 📌 Overview
This project is a **Smart Plant Monitoring & Care System** that:
- Collects **real-time sensor data** (soil moisture, temperature, humidity, light intensity) from an **ESP module**.
- Stores a **plant dataset** in **MongoDB** with ideal environmental conditions for 1000+ plant species.
- Compares real-time sensor data with plant requirements and provides **care suggestions** (e.g., increase watering, move to shade, etc.).
- Sends soil moisture data to a **Flask server**, which controls a **water pump relay** based on conditions.

## 🏗️ Project Architecture
*(Insert a system architecture diagram showing how the ESP module, Flask server, MongoDB, and website interact.)*

## 🖥️ Features
✅ **Real-time Sensor Data Monitoring**  
✅ **Plant Database for Condition Matching**  
✅ **Automated Watering Control**  
✅ **API-Based Data Exchange Between Flask & Website**  
✅ **User-Friendly Dashboard to View Suggestions**  

## 🛠️ Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Hardware**: ESP Module (for sensor readings), Relay Module (for water pump)
- **API Communication**: REST API for data exchange

## ⚙️ Setup Instructions
### 1️⃣ Clone the Repository
```sh
 git clone https://github.com/yourusername/your-repo-name.git
 cd your-repo-name
```

### 2️⃣ Install Dependencies
```sh
 pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables
Create a `.env` file in the root directory and set the following:
```env
MONGO_URI=your_mongo_connection_string
FRIEND_SERVER_URL=http://your-flask-server-url.com/sensor_data
```

### 4️⃣ Start the Flask Server
```sh
 python Backend_server.py
```

### 5️⃣ Start the Frontend (Optional)
Serve your frontend files using a simple HTTP server:
```sh
 Start with live server or Just double click the index.html
```
Then open `http://localhost:8000` in your browser.

## 🚀 API Endpoints
### 1️⃣ Compare Plant Conditions
- **Endpoint**: `POST /compare_plant`
- **Request Body**:
  ```json
  {
      "name": "Aloe Vera"
  }
  ```
- **Response Example**:
  ```json
  {
      "plant": {
          "_id": "67b765842548bb6d32e50040",
          "ideal_humidity": 39.47,
          "ideal_light": 38632.53,
          "ideal_moisture": 39.13,
          "ideal_temperature": 15.59
      },
      "sensor_data": {
          "humidity": 55,
          "light_intensity": 450,
          "soil_moisture": 40,
          "temperature": 26
      },
      "suggestions": [
          "Reduce watering 🚫💧",
          "Decrease temperature ❄️",
          "Decrease humidity 💨",
          "Move plant to more light ☀️"
      ],
      "data_source": "real"
  }
  ```

## 🔧 Future Improvements
- [ ] **User Authentication** (Login-based personalized plant care tracking)
- [ ] **Mobile App** (View plant conditions from anywhere)
- [ ] **Machine Learning Model** (Predict watering needs based on trends)
- [ ] **Cloud Storage** (Remote database & analytics dashboard)

## 📷 Screenshots
*(Insert UI screenshots of the website and API response results.)*

## 💡 Contributors
- **Himanshu Yadav** - Website & MongoDB Integration
- **Tanish Sidana** - Flask API & ESP Server
- **Rajveer Singh Shekhawat & Geet Gaggar** - Circuit Architecture & Arduino Code

## 📜 License
This project is **open-source**.

---
🌱 Happy Coding & Plant Caring! 🌿

