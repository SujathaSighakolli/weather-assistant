# Weather API integration logic
# utils/weather_api.py

import requests
import os

from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_weather_data(city, unit="metric"):
    try:
        url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units={unit}"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Weather Error: {e}")
        return None


def get_forecast_data(city, unit="metric"):
    try:
        url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units={unit}"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Forecast Error: {e}")
        return None


def get_aqi_data(city):
    try:
        # Get coordinates first
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_res = requests.get(geo_url).json()
        if not geo_res:
            return None
        lat, lon = geo_res[0]['lat'], geo_res[0]['lon']

        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_res = requests.get(aqi_url)
        aqi_res.raise_for_status()
        return aqi_res.json()
    except Exception as e:
        print(f"AQI Error: {e}")
        return None
