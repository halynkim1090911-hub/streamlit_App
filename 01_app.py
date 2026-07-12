import streamlit as st
import requests
from PIL import Image

# OpenWeatherMap API Key
API_KEY = st.secrets["API_KEY"]

st.set_page_config(page_title="오늘 뭐 입지?", page_icon="👕")

st.title("🌤️ 오늘 뭐 입지?")
st.write("오늘의 날씨를 확인하고 옷차림을 추천받으세요.")

city = st.text_input("도시를 입력하세요", "Seoul")

if st.button("날씨 확인"):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"

    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        weather = data["weather"][0]["description"]

        st.subheader("📌 오늘의 날씨")
        st.write(f"🌡️ 기온 : **{temp}°C**")
        st.write(f"☁️ 날씨 : **{weather}**")
        st.write(f"💧 습도 : **{humidity}%**")

        st.divider()

        st.subheader("👕 추천 옷차림")

        if temp >= 28:
            st.success("민소매, 반팔, 반바지를 추천합니다.")
            st.image("images/shorts.png", width=250)

        elif temp >= 23:
            st.success("반팔과 얇은 셔츠를 추천합니다.")
            st.image("images/tshirt.png", width=250)

        elif temp >= 20:
            st.success("긴팔 셔츠를 추천합니다.")
            st.image("images/shirt.png", width=250)

        elif temp >= 17:
            st.success("얇은 가디건 또는 후드티를 추천합니다.")
            st.image("images/hoodie.png", width=250)

        elif temp >= 12:
            st.success("자켓을 추천합니다.")
            st.image("images/jacket.png", width=250)

        else:
            st.success("두꺼운 코트를 추천합니다.")
            st.image("images/coat.png", width=250)

        if "비" in weather:
            st.warning("☔ 우산을 챙기세요.")
            st.image("images/umbrella.png", width=180)

    else:
        st.error("도시를 찾을 수 없습니다.")
