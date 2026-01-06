"""
Tool definitions for the AI assistant.
Tools are functions that the LLM can call to get external data.
"""

import os
import httpx
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.
    
    Args:
        city: The name of the city to get weather for (e.g., "London", "Tokyo", "New York")
    
    Returns:
        A string describing the current weather conditions.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key or api_key == "your_weather_api_key_here":
        return "Error: Weather API key not configured. Please add WEATHER_API_KEY to your .env file."
    
    try:
        # Call the WeatherAPI
        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": city,
            "aqi": "no"
        }
        
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        location = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]
        
        return f"""Weather for {location}, {country}:
🌡️ Temperature: {temp_c}°C ({temp_f}°F)
☁️ Condition: {condition}
💧 Humidity: {humidity}%
💨 Wind: {wind_kph} km/h"""
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return f"Sorry, I couldn't find weather data for '{city}'. Please check the city name."
        return f"Error fetching weather: {e}"
    except httpx.RequestError as e:
        return f"Network error: Could not connect to weather service. {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


# List of all available tools
TOOLS = [get_weather]
