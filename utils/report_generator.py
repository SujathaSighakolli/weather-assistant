# AI chatbot using GPT/Granite logic
# utils/report_generator.py

from fpdf import FPDF
from io import BytesIO


def generate_pdf_report(weather, forecast, aqi):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    city = weather['name']
    temp = weather['main']['temp']
    desc = weather['weather'][0]['description']
    humidity = weather['main']['humidity']
    wind = weather['wind']['speed']
    aqi_val = aqi['list'][0]['main']['aqi'] if aqi else "N/A"

    pdf.cell(200, 10, txt=f"Weather Report for {city}", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Current Temperature: {temp}°", ln=True)
    pdf.cell(200, 10, txt=f"Description: {desc}", ln=True)
    pdf.cell(200, 10, txt=f"Humidity: {humidity}%", ln=True)
    pdf.cell(200, 10, txt=f"Wind Speed: {wind} km/h", ln=True)
    pdf.cell(200, 10, txt=f"Air Quality Index: {aqi_val}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(200, 10, txt="Forecast (next 5 intervals):", ln=True)
    pdf.set_font("Arial", size=11)

    for entry in forecast['list'][:5]:
        time = entry['dt_txt']
        temp_f = entry['main']['temp']
        desc_f = entry['weather'][0]['description']
        pdf.cell(200, 10, txt=f"{time}: {temp_f}°, {desc_f}", ln=True)

    output = BytesIO()
    pdf.output(output)
    return output.getvalue()
