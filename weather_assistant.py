# ===== Step 1: Imports and Setup =====

import streamlit as st
import warnings
warnings.filterwarnings("ignore")
import streamlit.components.v1 as components
import requests
import os
import json
import pyttsx3
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv
from gtts import gTTS
import tempfile

# Set page configuration
st.set_page_config(page_title="🌤️ WeatherEase", layout="wide")
# ===== Load .env file with API Key =====
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Language options
languages = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "తెలుగు (Telugu)": "te",
    "தமிழ் (Tamil)": "ta",
    "ಕನ್ನಡ (Kannada)": "kn",
    "മലയാളം (Malayalam)": "ml"
}

# Load translations
with open("translations.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

# Load language-based font styles
font_data = {
    "en": {
        "font_family": "'Poppins', sans-serif",
        "font_url": "https://fonts.googleapis.com/css2?family=Poppins&display=swap"
    },
    "hi": {
        "font_family": "'Noto Sans Devanagari', sans-serif",
        "font_url": "https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari&display=swap"
    },
    "te": {
        "font_family": "'Noto Sans Telugu', sans-serif",
        "font_url": "https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu&display=swap"
    },
    "ta": {
        "font_family": "'Noto Sans Tamil', sans-serif",
        "font_url": "https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil&display=swap"
    },
    "kn": {
        "font_family": "'Noto Sans Kannada', sans-serif",
        "font_url": "https://fonts.googleapis.com/css2?family=Noto+Sans+Kannada&display=swap"
    },
    "ml": {
        "font_family": "'Noto Sans Malayalam', sans-serif",
        "font_url": "https://fonts.googleapis.com/css2?family=Noto+Sans+Malayalam&display=swap"
    }
}

# Language selector
selected_lang = st.sidebar.selectbox("🌐 Select Language", options=list(languages.keys()), index=0)
lang_code = languages[selected_lang]
theme = st.sidebar.radio("🎨 Select Theme", ["Light", "Dark", "Auto"])

# Translation function
def t(text):
    return translations.get(text, {}).get(lang_code, text)

# Apply custom font
font_url = font_data.get(lang_code, font_data['en'])['font_url']
font_family = font_data.get(lang_code, font_data['en'])['font_family']

st.markdown(f'<link href="{font_url}" rel="stylesheet">', unsafe_allow_html=True)
st.markdown(f"""
    <style>
    html, body, [class*="css"] {{
        font-family: {font_family} !important;
    }}
    </style>
""", unsafe_allow_html=True)
# App title and caption
st.markdown(f"""
    <h1 style='text-align: center;'>{t('WeatherEase 🌤️')}</h1>
    <p style='text-align: center; font-size: 18px; color: gray;'>{t('Your daily weather guide made simple.')}</p>
""", unsafe_allow_html=True)

def apply_gradient(condition=None, theme="Auto"):
    gradients = {
        "Light": {
            "clear": "linear-gradient(to right, #f6d365, #cbd8e8)",     # sunny
            "cloud": "linear-gradient(to right, #bdc3c7, #adc6e5)",     # cloudy
            "rain": "linear-gradient(to right, #83a4d4, #3785d8)",      # rainy
            "snow": "linear-gradient(to right, #e6dada, #1c1dab)",      # snow
            "default": "linear-gradient(to right, #434343, #1e0f75)"    # fallback
        },
        "Dark": {
            "clear": "linear-gradient(to right, #f6d365, #b589d6)",     # sunny
            "cloud": "linear-gradient(to right, #bdc3c7, #9969c7)",     # cloudy
            "rain": "linear-gradient(to right, #83a4d4, #804fb3)",      # rainy
            "snow": "linear-gradient(to right, #e6dada, #6a359c)",      # snow
            "default": "linear-gradient(to right, #434343, #552586)"    # fallback
        },
        "Auto": {
            "clear": "linear-gradient(to right, #f6d365, #f1b04c)",     # sunny
            "cloud": "linear-gradient(to right, #bdc3c7, #ee9f27)",     # cloudy
            "rain": "linear-gradient(to right, #83a4d4, #bb7800)",      # rainy
            "snow": "linear-gradient(to right, #e6dada, #764c00)",      # snow
            "default": "linear-gradient(to right, #434343, #523500)"    # fallback
        }
    }

    key = "default"
    if condition:
        cond = condition.lower()
        if "clear" in cond:
            key = "clear"
        elif "cloud" in cond:
            key = "cloud"
        elif "rain" in cond:
            key = "rain"
        elif "snow" in cond:
            key = "snow"

    if theme in ["Light", "Dark"]:
        bg = gradients[theme].get(key, gradients[theme]["default"])
        font_color = "#000000" if theme == "Light" else "#FFFFFF"
    else:  # Auto
        bg = gradients["Auto"].get(key, gradients["Auto"]["default"])
        font_color = "#FFFFFF"

    st.markdown(f"""
        <style>
        .stApp {{
            background: {bg};
            background-attachment: fixed;
            background-size: cover;
            color: {font_color};
        }}
        h1, h2, h3, h4, h5, h6,
        .stTextInput > label,
        .stSelectbox > label,
        .stRadio > label,
        .stButton > button {{
            color: {font_color};
        }}
        </style>
    """, unsafe_allow_html=True)

def get_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

def get_forecast_data(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None
from fpdf import FPDF
from fpdf.enums import XPos, YPos

def generate_simple_pdf(report_data, city):
    filename = f"{city}_weather_report.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Title
    pdf.set_text_color(40, 40, 40)
    pdf.cell(
        w=0, h=10, 
        text="Weather Report", 
        new_x=XPos.LMARGIN, new_y=YPos.NEXT, 
        align='C'
    )
    pdf.ln(5)

    # Content
    for key, value in report_data.items():
        pdf.cell(
            w=0, h=10, 
            text=f"{key}: {value}", 
            new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )

    pdf.output(filename)
    return filename

import threading
import pyttsx3

def speak_weather_summary(text, lang_code="en"):
    def run_tts():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)

            # Get available voices
            voices = engine.getProperty('voices')

            lang_voice_map = {
                "hi": ["hindi", "hi"],
                "te": ["telugu", "te"],
                "ta": ["tamil", "ta"],
                "kn": ["kannada", "kn"],
                "ml": ["malayalam", "ml"],
                "en": ["english", "en"]
            }

            matched = False
            if lang_code in lang_voice_map:
                for voice in voices:
                    for keyword in lang_voice_map[lang_code]:
                        if keyword in voice.name.lower() or keyword in voice.id.lower():
                            engine.setProperty('voice', voice.id)
                            matched = True
                            break
                    if matched:
                        break

            if not matched:
                print(f"[INFO] Voice not found for {lang_code}, using default.")

            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("❌ TTS Error:", e)

    # Run in background to avoid blocking
    threading.Thread(target=run_tts).start()
from datetime import datetime, timezone as dt_timezone
from pytz import timezone
import tempfile
from gtts import gTTS
import streamlit as st
import streamlit.components.v1 as components

# 🔊 Speak text using gTTS
def speak_gtts(text, lang_code="en"):
    try:
        tts = gTTS(text=text, lang=lang_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            st.audio(fp.name, format="audio/mp3")
    except Exception as e:
        st.error("🔊 TTS Error: " + str(e))

# 🌆 City input box
city = st.text_input("🎤 " + t("Type the city name"), value=st.session_state.get("city_input", ""), key="city_input")

# Sync session state with recognized voice city
if city:
    st.session_state["city"] = city

    data = get_weather_data(city)
    if data:
        condition = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]
        apply_gradient(condition, theme)

        emoji = "☁️"
        if "rain" in condition: emoji = "🌧️"
        elif "clear" in condition: emoji = "☀️"
        elif "snow" in condition: emoji = "❄️"

        # 🌇 Timezone-aware conversion to IST
        ist = timezone("Asia/Kolkata")
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"], tz=dt_timezone.utc).astimezone(ist).strftime("%H:%M IST")
        sunset = datetime.fromtimestamp(data["sys"]["sunset"], tz=dt_timezone.utc).astimezone(ist).strftime("%H:%M IST")

        # 🧾 Weather Card UI
        st.markdown(f"""
        <div style="background-color:rgba(255,255,255,0.2);padding:2rem;border-radius:15px;margin-top:20px;">
            <h2>{emoji} {t('Current Weather in')} {city.title()}</h2>
            <p>🌡️ {t('Temperature')}: <b>{temp}°C</b></p>
            <p>💧 {t('Humidity')}: <b>{data['main']['humidity']}%</b></p>
            <p>🌬️ {t('Wind Speed')}: <b>{data['wind']['speed']} m/s</b></p>
            <p>🌅 {t('Sunrise')}: <b>{sunrise}</b></p>
            <p>🌇 {t('Sunset')}: <b>{sunset}</b></p>
            <p>📝 {t('Condition')}: <b>{condition.title()}</b></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ " + t("Could not fetch weather data."))
else:
    st.info(t("ℹ️ Please enter a city name."))

# Step 4: Add Horizontal Tabs for more features

tabs = st.tabs([
    "📍 " + t("Map View"),
    "📊 " + t("Multi-city Comparison"),
    "📅 " + t("5-day Forecast"),
    "📈 " + t("Hourly Forecast"),
    "📥 " + t("Download Report"),
    "🧠 " + t("AI Suggestions"),
    "🎙️ " + t("Voice Summary")
])


# ========== Tab 1: Map View ==========
with tabs[0]:
    st.subheader("📍 " + t("Map View"))
    st.markdown(t("🌐 Displaying your selected city on the map."))

    city = st.session_state.get("city", "")  # Get city from session state if previously entered

    if city:
        data = get_weather_data(city)
        if data and "coord" in data:
            lat = data["coord"]["lat"]
            lon = data["coord"]["lon"]

            m = folium.Map(location=[lat, lon], zoom_start=10)
            folium.Marker([lat, lon], tooltip=city.title()).add_to(m)
            st_data = st_folium(m, width=1000, height=400)
        else:
            st.warning(t("⚠️ Unable to fetch map data. Please check the city name or try again."))
    else:
        st.info(t("ℹ️ Please enter a city name in the Current Weather tab to load the map."))


# ========== Tab 2: Multi-city Comparison ==========
with tabs[1]:
    st.subheader("📊 " + t("Multi-city Comparison"))
    st.markdown(t("Compare temperature across selected cities."))

    city_list = st.multiselect(t("Choose cities to compare"), ["Hyderabad", "Mumbai", "Delhi", "Chennai", "Bangalore", "Kochi"])
    if city_list:
        temp_data = []
        for c in city_list:
            d = get_weather_data(c)
            if d:
                temp_data.append({"City": c, "Temp": d["main"]["temp"]})
        df = pd.DataFrame(temp_data)
        st.plotly_chart(px.bar(df, x="City", y="Temp", title=t("Temperature Comparison")))

# ========== Tab 3: 5-Day Forecast ==========
with tabs[2]:
    st.subheader("📅 " + t("5-day Forecast"))
    forecast = get_forecast_data(city)
    if forecast and "list" in forecast:
        forecast_df = pd.DataFrame(forecast["list"])
        forecast_df["dt_txt"] = pd.to_datetime(forecast_df["dt_txt"])
        forecast_df["temp"] = forecast_df["main"].apply(lambda x: x["temp"])
        st.plotly_chart(px.line(forecast_df, x="dt_txt", y="temp", title=t("5-day Forecast")))

## ========== Tab 4: Hourly Forecast ==========
with tabs[3]:
    forecast_data = get_forecast_data(city)
    if forecast_data and "list" in forecast_data:
        st.subheader("📈 " + t("Hourly Forecast"))
        
        df = pd.DataFrame(forecast_data["list"])
        df["Time"] = pd.to_datetime(df["dt_txt"])
        df["Temperature (°C)"] = df["main"].apply(lambda x: x["temp"])
        df["Humidity (%)"] = df["main"].apply(lambda x: x["humidity"])

        fig_temp = px.line(df.head(12), x="Time", y="Temperature (°C)",
                           title=t("Temperature Trend"), markers=True)
        fig_humidity = px.line(df.head(12), x="Time", y="Humidity (%)",
                               title=t("Humidity Trend"), markers=True)

        st.plotly_chart(fig_temp, use_container_width=True)
        st.plotly_chart(fig_humidity, use_container_width=True)
    else:
        st.warning(t("Hourly forecast not available."))


# ========== Tab 5: Download Report ==========
    from pytz import timezone
from datetime import datetime, timezone as dt_timezone

with tabs[4]:
    st.subheader("📥 " + t("Download Report"))

    city = st.session_state.get("city", "")
    if city:
        data = get_weather_data(city)
        if data:
            # ✅ Convert UTC to IST using timezone-aware datetime
            ist = timezone('Asia/Kolkata')
            sunrise_utc = datetime.fromtimestamp(data["sys"]["sunrise"], dt_timezone.utc)
            sunset_utc = datetime.fromtimestamp(data["sys"]["sunset"], dt_timezone.utc)
            sunrise_ist = sunrise_utc.astimezone(ist).strftime("%H:%M IST")
            sunset_ist = sunset_utc.astimezone(ist).strftime("%H:%M IST")

            # ✅ Report data in English for PDF (PDF only supports English)
            english_report_data = {
                "City": city.title(),
                "Temperature": f"{data['main']['temp']} °C",
                "Humidity": f"{data['main']['humidity']}%",
                "Weather Condition": data["weather"][0]["description"].title(),
                "Wind Speed": f"{data['wind']['speed']} m/s",
                "Sunrise": sunrise_ist,
                "Sunset": sunset_ist,
            }

            # ✅ Show localized data on screen
            report_data = {
                t("City"): city.title(),
                t("Temperature"): f"{data['main']['temp']} °C",
                t("Humidity"): f"{data['main']['humidity']}%",
                t("Weather Condition"): data["weather"][0]["description"].title(),
                t("Wind Speed"): f"{data['wind']['speed']} m/s",
                t("Sunrise"): sunrise_ist,
                t("Sunset"): sunset_ist,
            }

            st.markdown("### 🌤️ ***" + t("Weather Summary") + "***")
            for key, val in report_data.items():
                st.markdown(f"<p style='font-weight:bold;font-style:italic;'>{key}: {val}</p>", unsafe_allow_html=True)

            # ✅ Show a warning for non-English languages
            if lang_code != "en":
                st.warning(t("⚠️ Note: The downloaded PDF report will be in English only."))

            # ✅ Generate and download PDF
            if st.button("📄 " + t("Generate PDF Report")):
                filename = generate_simple_pdf(english_report_data, city)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="📄 " + t("Download Report PDF"),
                        data=file,
                        file_name=filename,
                        mime="application/pdf"
                    )
        else:
            st.warning(t("⚠️ Could not fetch weather data."))
    else:
        st.warning(t("Please enter a valid city to generate report."))

with tabs[5]:
    st.subheader("🧠 " + t("AI Suggestions"))

    city = st.session_state.get("city", "")
    if city:
        data = get_weather_data(city)

        if data:
            temp = data["main"]["temp"]
            condition = data["weather"][0]["description"].lower()

            # Theme styles
            card_styles = {
                "Light": {"bg": "#eef6ff", "text": "#000000", "border": "#cce0ff"},
                "Dark": {"bg": "#1e1e2f", "text": "#ffffff", "border": "#4d4d66"},
                "Auto": {"bg": "#2c3e50", "text": "#ffffff", "border": "#5a7894"}
            }
            style = card_styles.get(theme, card_styles["Auto"])

            # Titles for each condition
            suggestion_titles = {
                "rain": t("🌧️ Rainy Today"),
                "clear_hot": t("☀️ Hot and Sunny"),
                "clear_cool": t("🌤️ Cool and Clear"),
                "snow": t("❄️ Snowy Weather"),
                "cloud": t("☁️ Cloudy Today"),
                "storm": t("⛈️ Thunderstorm Today"),
                "default": t("🧥 Weather Tips")
            }

            # Bullet tips
            suggestion_lists = {
                "rain": [
                    t("Wear raincoat and waterproof shoes"),
                    t("Carry an umbrella"),
                    t("Avoid drying clothes outside"),
                    t("Drive safely on wet roads")
                ],
                "clear_hot": [
                    t("Wear sunglasses and use sunscreen"),
                    t("Stay hydrated throughout the day"),
                    t("Wear light cotton clothes"),
                    t("Avoid going out at noon")
                ],
                "clear_cool": [
                    t("Ideal for outdoor activities"),
                    t("Great day to dry clothes"),
                    t("No jacket needed today"),
                    t("Enjoy a walk in nature")
                ],
                "snow": [
                    t("Wear thermal clothing and boots"),
                    t("Avoid non-essential travel"),
                    t("Keep heaters and blankets ready"),
                    t("Not good for drying clothes")
                ],
                "cloud": [
                    t("Mild temperature — dress comfortably"),
                    t("Carry a light jacket"),
                    t("Good day for a walk"),
                    t("May take longer to dry clothes")
                ],
                "storm": [
                    t("Wear raincoat and boots"),
                    t("Don’t dry clothes outside"),
                    t("Stay indoors and unplug devices"),
                    t("Drive carefully")
                ],
                "default": [
                    t("Check forecast before going out"),
                    t("Carry umbrella or jacket"),
                    t("Dress in layers"),
                    t("Keep weather apps handy")
                ]
            }

            # Determine condition type
            if "storm" in condition or "thunder" in condition:
                key = "storm"
            elif "rain" in condition:
                key = "rain"
            elif "clear" in condition:
                key = "clear_hot" if temp > 30 else "clear_cool"
            elif "snow" in condition:
                key = "snow"
            elif "cloud" in condition or "overcast" in condition:
                key = "cloud"
            else:
                key = "default"

            # Final content
            title = suggestion_titles[key]
            tips = suggestion_lists[key]
            full_text = f"{title}. " + ". ".join(tips)

            # Render styled box
            st.markdown(f"""
                <div style="background:{style['bg']}; color:{style['text']}; 
                            padding:20px; border-radius:12px; border:2px solid {style['border']};">
                    <h4 style="margin-bottom: 10px;">{title}</h4>
                    <ul style="font-size: 16px; line-height: 1.7;">
                        {''.join([f"<li>{tip}</li>" for tip in tips])}
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            # Speak in selected language
            if st.button("🔊 " + t("Speak This")):
                speak_gtts(full_text, lang_code)
        else:
            st.warning(t("⚠️ Could not fetch weather data for suggestions."))
    else:
        st.info(t("ℹ️ Please enter a city name in the Current Weather tab."))

with tabs[6]:
    st.subheader("🎙️ " + t("Voice Summary"))

    city = st.session_state.get("city", "")
    if city:
        data = get_weather_data(city)  # ✅ This ensures `data` is defined

        if data:
            summary = (
                f"{t('Weather in')} {city.title()}: "
                f"{data['weather'][0]['description'].title()}, "
                f"{t('Temperature')}: {data['main']['temp']}°C, "
                f"{t('Humidity')}: {data['main']['humidity']}%, "
                f"{t('Wind Speed')}: {data['wind']['speed']} m/s"
            )
            st.markdown(f"📝 **{t('Summary')}**: _{summary}_")

            if st.button("🔊 " + t("Play Voice Summary")):
                speak_gtts(summary, lang_code)  # Use your TTS function
        else:
            st.warning(t("⚠️ Could not fetch weather data."))
    else:
        st.info(t("ℹ️ Please enter a city name in the Current Weather tab."))


# Step 5: Add final horizontal tabs for Favorites, Alerts, Accessibility
more_tabs = st.tabs([
    "⭐ " + t("Favorites"),
    "♿ " + t("Accessibility Options")
])

# ========== Tab 7: Favorites ==========
with more_tabs[0]:
    st.subheader("⭐ " + t("Favorites"))
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    add_fav = st.button(t("Add Current City to Favorites"))
    if add_fav and city not in st.session_state.favorites:
        st.session_state.favorites.append(city)

    if st.session_state.favorites:
        st.markdown("📌 " + t("Your Favorite Cities") + ":")
        for fav in st.session_state.favorites:
            st.write("🔹", fav)

# ========== Accessibility Options ==========
with more_tabs[1]:  # ♿ Accessibility Options tab
    st.subheader("♿ " + t("Accessibility Options"))
    font_size = st.slider(t("Select Font Size"), 12, 36, 18)

    st.markdown(f"""
        <style>
        html, body, [class*="css"] {{
            font-size: {font_size}px !important;
        }}
        </style>
    """, unsafe_allow_html=True)


# ========== Footer ==========
st.markdown("""<hr style="border-top: 2px solid #bbb;">""", unsafe_allow_html=True)

st.markdown(f"""
<center>
    🛠️ {t("Built with ❤️ using")} <a href="https://streamlit.io" target="_blank">Streamlit</a> | 
    🌐 {t("Language")}: {selected_lang} | 
    🎨 {t("Theme")}: {theme} <br><br>
    📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</center>
""", unsafe_allow_html=True)
