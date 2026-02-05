rt streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv

# 1. SETUP & THEMING
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(page_title="SkyMood Pro", page_icon="🌤️", layout="wide")

# Custom CSS for a professional portfolio look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #00d4ff;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HELPER FUNCTIONS
def get_mood(condition):
    moods = {
        "Clear": "☀️ Energetic & Productive",
        "Clouds": "☁️ Chill & Focused",
        "Rain": "🌧️ Creative & Reflective",
        "Snow": "❄️ Peaceful & Calm",
        "Thunderstorm": "⛈️ Intense & Bold",
        "Drizzle": "🌦️ Light & Relaxed"
    }
    return moods.get(condition, "😊 Balanced & Ready")

def fetch_weather_data(city):
    city = city.strip()
    # Current Weather
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    curr_res = requests.get(base_url, params=params).json()
    
    # 5-Day Forecast
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    fore_res = requests.get(forecast_url, params=params).json()
    
    return curr_res, fore_res

# 3. SIDEBAR NAVIGATION
st.sidebar.title("📍 SkyMood Control")
st.sidebar.markdown("Explore weather and mood vibes.")
target_city = st.sidebar.text_input("Enter City Name", "London")

st.sidebar.markdown("---")
st.sidebar.subheader("🌎 Quick Access")
if st.sidebar.button("New York"): target_city = "New York"
if st.sidebar.button("Tokyo"): target_city = "Tokyo"
if st.sidebar.button("Paris"): target_city = "Paris"

# 4. MAIN DASHBOARD LOGIC
if target_city:
    data, f_data = fetch_weather_data(target_city)
    
    if data.get("cod") == 200:
        col_main, col_forecast = st.columns([3, 1])
        
        with col_main:
            st.title(f"Weather in {target_city.title()}, {data['sys']['country']}")
            st.subheader(f"Mood: {get_mood(data['weather'][0]['main'])}")
            
            # Key Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Temp", f"{data['main']['temp']}°C")
            m2.metric("Feels Like", f"{data['main']['feels_like']}°C")
            m3.metric("Humidity", f"{data['main']['humidity']}%")
            m4.metric("Wind Speed", f"{data['wind']['speed']} m/s")

            # --- PLOTLY CHART ---
            st.markdown("### 🌡️ 5-Day Temperature Trend")
            chart_list = []
            for item in f_data['list']:
                chart_list.append({
                    "Time": item['dt_txt'],
                    "Temp (°C)": item['main']['temp'],
                    "Weather": item['weather'][0]['main']
                })
            df = pd.DataFrame(chart_list)
            
            fig = px.line(df, x="Time", y="Temp (°C)", 
                          hover_data=["Weather"], 
                          markers=True, 
                          template="plotly_dark")
            fig.update_traces(line_color='#00d4ff')
            st.plotly_chart(fig, use_container_width=True)

            # --- DATA DOWNLOAD ---
            st.markdown("### 📊 Export Forecast")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Forecast as CSV",
                data=csv,
                file_name=f"{target_city}_weather.csv",
                mime="text/csv"
            )

        with col_forecast:
            st.subheader("🕒 Daily Peaks")
            midday = [i for i in f_data['list'] if "12:00:00" in i['dt_txt']]
            for day in midday:
                date = datetime.strptime(day['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%a, %b %d')
                st.write(f"**{date}**")
                st.write(f"{day['main']['temp']}°C | {day['weather'][0]['main']}")
                st.divider()

    else:
        st.error(f"⚠️ Error: {data.get('message', 'City not found').title()}")

# 5. FOOTER
st.markdown("---")
st.caption("🚀 Developed for Portfolio | Powered by OpenWeatherMap API")
