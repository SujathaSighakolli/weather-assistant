# Gradient and UI logic for light/dark/auto
# utils/ui_components.py

import streamlit as st

# Gradient map by theme and weather
GRADIENTS = {
    "Light": {
        "Clear": "linear-gradient(to right, #fffbd5, #b20a2c)",
        "Clouds": "linear-gradient(to right, #e0eafc, #cfdef3)",
        "Rain": "linear-gradient(to right, #cfd9df, #e2ebf0)",
        "Snow": "linear-gradient(to right, #fdfbfb, #ebedee)",
        "Night": "linear-gradient(to right, #e0c3fc, #8ec5fc)",
        "Default": "linear-gradient(to right, #fefcea, #f1da36)"
    },
    "Dark": {
        "Clear": "linear-gradient(to right, #42275a, #734b6d)",
        "Clouds": "linear-gradient(to right, #3E5151, #DECBA4)",
        "Rain": "linear-gradient(to right, #485563, #29323c)",
        "Snow": "linear-gradient(to right, #373b44, #4286f4)",
        "Night": "linear-gradient(to right, #0f2027, #203a43, #2c5364)",
        "Default": "linear-gradient(to right, #232526, #414345)"
    },
    "Auto": {
        "Clear": "linear-gradient(to right, #fceabb, #f8b500)",
        "Clouds": "linear-gradient(to right, #bdc3c7, #2c3e50)",
        "Rain": "linear-gradient(to right, #83a4d4, #b6fbff)",
        "Snow": "linear-gradient(to right, #e6dada, #274046)",
        "Night": "linear-gradient(to right, #141e30, #243b55)",
        "Default": "linear-gradient(to right, #d7d2cc, #304352)"
    }
}


def apply_gradient_theme(theme, condition):
    bg = GRADIENTS.get(theme, GRADIENTS["Auto"]).get(condition, GRADIENTS[theme]["Default"])
    st.markdown(f"""
        <style>
        .stApp {{
            background: {bg};
            background-attachment: fixed;
            background-size: cover;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_weather_cards(weather, forecast, aqi, unit):
    temp = weather['main']['temp']
    desc = weather['weather'][0]['description'].title()
    icon = weather['weather'][0]['icon']
    humidity = weather['main']['humidity']
    wind = weather['wind']['speed']
    aqi_value = aqi['list'][0]['main']['aqi'] if aqi else "N/A"

    unit_symbol = "°C" if unit == "metric" else "°F"

    st.markdown("""
    <div style='display: flex; gap: 1rem;'>
        <div class='card glass'>
            <h2>{temp} {unit}</h2>
            <p>{desc}</p>
            <p>Humidity: {humidity}% | Wind: {wind} km/h</p>
            <p>AQI: {aqi_value}</p>
        </div>
    </div>
    """.format(temp=temp, unit=unit_symbol, desc=desc, humidity=humidity, wind=wind, aqi_value=aqi_value), unsafe_allow_html=True)
