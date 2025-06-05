import requests
import os
import string

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") 
def clean_city_name(city):
    # Remove punctuation and extra whitespace
    return city.translate(str.maketrans('', '', string.punctuation)).strip()
def get_weather(city):
    if not WEATHER_API_KEY:
        return "Weather API key not found."

    city = clean_city_name(city)  # Clean the city input
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        description = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The current weather in {city} is {description} with a temperature of {temp}°C."
    else:
        return f"Sorry, I couldn't retrieve weather data for {city}."
