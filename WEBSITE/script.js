document.addEventListener('DOMContentLoaded', () => {
    const plantNameInput = document.getElementById('plantName');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultCard = document.getElementById('resultCard');

    // Elements for displaying data
    const recommendedMoisture = document.getElementById('recommendedMoisture');
    const currentMoisture = document.getElementById('currentMoisture');
    const currentTemp = document.getElementById('currentTemp');
    const currentHumidity = document.getElementById('currentHumidity');
    const currentLight = document.getElementById('currentLight');
    const careSuggestion = document.getElementById('careSuggestion');

    submitBtn.addEventListener('click', async () => {
        const plantName = plantNameInput.value.trim();
        
        if (!plantName) {
            alert('Please enter a plant name');
            return;
        }

        // Show loading indicator and hide results
        loadingIndicator.classList.remove('hidden');
        resultCard.classList.add('hidden');

        try {
            const response = await fetch('http://192.168.0.52:5002/compare_plant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: plantName })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Update UI with received data
            recommendedMoisture.textContent = data.plant?.ideal_moisture ? `${data.plant.ideal_moisture}%` : "No Data";
            recommendedHumidity.textContent = data.plant?.ideal_humidity ? `${data.plant.ideal_humidity}%` : "No Data";
            recommendedLight.textContent = data.plant?.ideal_light ? `${data.plant.ideal_light} lux` : "No Data";
            recommendedTemperature.textContent = data.plant?.ideal_temperature ? `${data.plant.ideal_temperature}°C` : "No Data";
            currentMoisture.textContent = data.sensor_data?.soil_moisture ? `${data.sensor_data.soil_moisture}%` : "No Data";
            currentTemp.textContent = data.sensor_data?.temperature ? `${data.sensor_data.temperature}°C` : "No Data";
            currentHumidity.textContent = data.sensor_data?.humidity ? `${data.sensor_data.humidity}%` : "No Data";
            currentLight.textContent = data.sensor_data?.light_intensity ? `${data.sensor_data.light_intensity} lux` : "No Data";
            careSuggestion.textContent = data.suggestions?.length ? data.suggestions.join(", ") : "No suggestion available";

            console.log("API Response:", data);

            // Show results
            resultCard.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to fetch plant data. Please try again.');
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    });

    // Allow form submission with Enter key
    plantNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitBtn.click();
        }
    });
}); 