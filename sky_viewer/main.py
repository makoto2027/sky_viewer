import streamlit as st
import requests
import json

with open("../config.json", "r") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return {
            "都市": data["name"],
            "天気": data["weather"][0]["description"],
            "気温": f"{data['main']['temp']}℃",
            "湿度": f"{data['main']['humidity']}%",
            "アイコン": data["weather"][0]["icon"]
        }
    else:
        return None

def get_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ja"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return {
            "都市": data["name"],
            "天気": data["weather"][0]["description"],
            "気温": f"{data['main']['temp']}℃",
            "湿度": f"{data['main']['humidity']}%",
            "アイコン": data["weather"][0]["icon"]
        }
    else:
        return None

def get_coords_by_ip():
    try:
        res = requests.get("https://ipinfo.io/json")
        if res.status_code == 200:
            loc = res.json().get("loc", "")  # "35.6895,139.6917" の形式
            lat, lon = loc.split(",")
            return lat, lon
    except:
        pass
    return None, None


# --- 初期化 ---
if "history" not in st.session_state:
    st.session_state.history = []


# Streamlit UI
st.title("☁️ 世界の空模様ビューワー")

city = st.text_input("都市名を入力してください（例：Tokyo）")

if st.button("🔍 天気を検索"):
    if city:
        weather = get_weather(city)
        if weather:
            # 結果表示
            st.subheader(f"📍 {weather['都市']}")
            st.write(f"天気：{weather['天気']}")
            st.write(f"気温：{weather['気温']}")
            st.write(f"湿度：{weather['湿度']}")
            st.image(f"http://openweathermap.org/img/wn/{weather['アイコン']}@2x.png")

            # 履歴に追加
            st.session_state.history.append({
                "都市": weather["都市"],
                "天気": weather["天気"],
                "気温": weather["気温"],
                "方法": "都市名"
            })
        else:
            st.error("天気情報の取得に失敗しました。")

# ✅ 現在地天気取得ボタン
if st.button("📍 現在地の天気を見る"):
    lat, lon = get_coords_by_ip()
    if lat and lon:
        weather = get_weather_by_coords(lat, lon)
        if weather:
            st.subheader(f"📍 あなたの現在地：{weather['都市']}")
            st.write(f"天気：{weather['天気']}")
            st.write(f"気温：{weather['気温']}")
            st.write(f"湿度：{weather['湿度']}")
            st.image(f"http://openweathermap.org/img/wn/{weather['アイコン']}@2x.png")

            # 履歴に追加
            st.session_state.history.append({
                "都市": weather["都市"],
                "天気": weather["天気"],
                "気温": weather["気温"],
                "方法": "現在地"
            })
        else:
            st.error("現在地の天気情報取得に失敗しました。")
    else:
        st.error("位置情報の取得に失敗しました。")

# --- 検索履歴 ---
st.markdown("### 🔁 検索履歴(最大5件)")
if st.session_state.history:
    for item in reversed(st.session_state.history[-5:]):
        st.write(f"📍 {item['都市']} - {item['天気']} / {item['気温']} （検索方法：{item['方法']}）")
else:
    st.write("履歴はまだありません。")