# Voice input and TTS support
# utils/audio_tools.py
import speech_recognition as sr
from gtts import gTTS
import os
import streamlit as st


def get_city_from_voice():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎙️ Listening for city name...")
            audio = recognizer.listen(source, timeout=5)
            city = recognizer.recognize_google(audio)
            st.success(f"You said: {city}")
            return city
    except Exception as e:
        st.error(f"Voice input failed: {e}")
        return None


def speak_weather_summary(weather):
    try:
        temp = weather['main']['temp']
        desc = weather['weather'][0]['description']
        city = weather['name']
        text = f"The weather in {city} is currently {desc} with a temperature of {temp} degrees."
        tts = gTTS(text=text)
        tts.save("weather.mp3")
        st.audio("weather.mp3")
    except Exception as e:
        st.error(f"Text-to-speech failed: {e}")
