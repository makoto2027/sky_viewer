from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from utils.weather_api import get_weather_by_city, get_weather_by_coords
from utils.db_manager import get_history, toggle_favorite, clear_history, add_history, get_latest_history, update_favorite
from datetime import timedelta, datetime
import requests
from typing import Optional, Dict
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "sessionflask")  # Use env var, fallback for dev only
app.permanent_session_lifetime = timedelta(days=1)  # Fixed typo

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            try:
                weather = get_weather_by_city(city)
            except Exception as e:
                logger.error(f"Weather API error: {e}")
                flash("天気情報の取得中にエラーが発生しました。")
                weather = None
            if weather:
                try:
                    data = {
                        "city": weather["都市"],
                        "weather": weather["天気"],
                        "temperature": weather["気温"],
                        "humidity": weather["湿度"],
                        "icon": weather["アイコン"],
                        "method": "都市名",
                        "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "favorite": 0
                    }
                    add_history(data)
                except Exception as e:
                    logger.error(f"DB error: {e}")
                    flash("履歴の保存中にエラーが発生しました。")
    return render_template("index.html", weather=weather, history=session["history"][-5:])

@app.route("/map")
def map_page():
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    return render_template("map.html", api_key=api_key)

@app.route("/weather")
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    method = request.args.get("method", "unknown")

    if not lat or not lon:
        return jsonify({"error": "緯度経度が指定されていません"}), 400

    try:
        weather_data = get_weather_by_coords(float(lat), float(lon))
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return jsonify({"error": "天気情報の取得中にエラーが発生しました。"}), 500

    if not weather_data or "error" in weather_data:
        return jsonify({"error": "天気情報を取得できませんでした"}), 500

    try:
        data = {
            "city": weather_data["都市"],
            "weather": weather_data["天気"],
            "temperature": weather_data["気温"],
            "humidity": weather_data["湿度"],
            "icon": weather_data["アイコン"],
            "method": method,
            "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "favorite": 0
        }
        add_history(data)
    except Exception as e:
        logger.error(f"DB error: {e}")
        # 履歴保存失敗は致命的でないので続行

    return jsonify(weather_data)

@app.route("/howto")
def howto():
    return render_template("howto.html")

@app.route("/add_favorite", methods=["POST"])
def add_favorite():
    method = request.form.get("method", "index")
    try:
        latest = get_latest_history()
        if latest:
            update_favorite(latest["id"], True)
            flash("お気に入りに登録しました！")
        else:
            flash("お気に入りに登録できる検索結果が見つかりませんでした。")
    except Exception as e:
        logger.error(f"DB error: {e}")
        flash("お気に入り登録中にエラーが発生しました。")

    if method == "map":
        return redirect(url_for("map_page"))
    else:
        return redirect(url_for("index"))

@app.route("/history")
def history():
    fav = request.args.get("fav", default=0, type=int)
    days = request.args.get("days", default=7, type=int)
    try:
        histories = get_history(only_favorites=bool(fav), days_limit=days)
    except Exception as e:
        logger.error(f"DB error: {e}")
        histories = []
        flash("履歴の取得中にエラーが発生しました。")
    return render_template("history.html", histories=histories, fav=fav, days=days)

@app.route("/toggle_favorite/<int:history_id>")
def toggle_fav(history_id: int):
    try:
        toggle_favorite(history_id)
    except Exception as e:
        logger.error(f"DB error: {e}")
        flash("お気に入り切り替え中にエラーが発生しました。")
    return redirect(url_for("history"))

@app.route("/clear_history")
def clear_all():
    try:
        clear_history()
    except Exception as e:
        logger.error(f"DB error: {e}")
        flash("履歴全削除中にエラーが発生しました。")
    return redirect(url_for("history"))

@app.route("/api/weather", methods=["GET"])
def api_weather():
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    try:
        if city:
            result = get_weather_by_city(city)
        elif lat and lon:
            result = get_weather_by_coords(float(lat), float(lon))
        else:
            return jsonify({"error": "Invalid parameters"}), 400
        if not result or "error" in result:
            return jsonify({"error": "天気情報を取得できませんでした"}), 500
        return jsonify(result)
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": "API呼び出し中にエラーが発生しました。"}), 500

@app.route("/api/weather_by_coords")
def api_weather_by_coords():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    logger.debug(f"[DEBUG] 受信座標: {lat}, {lon}")

    if lat and lon:
        try:
            weather = get_weather_by_coords(float(lat), float(lon))
            logger.debug(f"[DEBUG] 取得結果: {weather}")
            if weather and "都市" in weather:
                data = {
                    "city": weather["都市"],
                    "weather": weather["天気"],
                    "temperature": weather["気温"],
                    "humidity": weather["湿度"],
                    "icon": weather["アイコン"],
                    "method": "現在地",
                    "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "favorite": 0
                }
                add_history(data)
                return jsonify(weather)
            else:
                return jsonify({"error": "天気情報を取得できませんでした"}), 400
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({"error": "API呼び出し中にエラーが発生しました。"}), 500
    return jsonify({"error": "天気情報を取得できませんでした"}), 400

if __name__ == "__main__":
    app.run(debug=True)