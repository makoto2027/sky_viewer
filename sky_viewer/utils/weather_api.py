import requests
import os
import logging
from typing import Dict, Optional, Union
from datetime import datetime, timezone, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed. Please install it for .env file support.")

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
if not API_KEY:
    logger.error("OPENWEATHERMAP_API_KEY environment variable is not set")

JST = timezone(timedelta(hours=9))  # 日本時間（UTC+9）

# API configuration
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_PARAMS = {
    "appid": API_KEY,
    "units": "metric",
    "lang": "ja"
}

def _make_api_request(params: Dict[str, Union[str, float]]) -> Optional[Dict]:
    """
    Make API request to OpenWeatherMap with error handling
    
    Args:
        params: Query parameters for the API request
        
    Returns:
        API response data or None if request failed
    """
    if not API_KEY:
        logger.error("API key is not configured")
        return None
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return None
    except ValueError as e:
        logger.error(f"Invalid JSON response: {e}")
        return None

def _format_weather_data(data: Dict) -> Dict[str, str]:
    """
    Format weather data from API response
    
    Args:
        data: Raw API response data
        
    Returns:
        Formatted weather data dictionary
    """
    try:
        dt = datetime.fromtimestamp(data["dt"], JST).strftime("%H:%M")
        return {
            "都市": data["name"],
            "天気": data["weather"][0]["description"],
            "気温": f"{data['main']['temp']}℃",
            "湿度": f"{data['main']['humidity']}%",
            "アイコン": data["weather"][0]["icon"],
            "時刻": dt
        }
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected data format: {e}")
        return {"error": "Invalid data format"}

def get_weather_by_city(city: str) -> Optional[Dict[str, str]]:
    """
    Get weather information by city name
    
    Args:
        city: City name
        
    Returns:
        Weather data dictionary or None if request failed
    """
    if not city:
        logger.error("City name is required")
        return None
    
    params = {**DEFAULT_PARAMS, "q": city}
    data = _make_api_request(params)
    
    if data is None:
        return None
    
    return _format_weather_data(data)

def get_weather_by_coords(lat: float, lon: float) -> Optional[Dict[str, str]]:
    """
    Get weather information by coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Weather data dictionary or None if request failed
    """
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        logger.error("Latitude and longitude must be numeric values")
        return None
    
    params = {**DEFAULT_PARAMS, "lat": lat, "lon": lon}
    data = _make_api_request(params)
    
    if data is None:
        return None
    
    return _format_weather_data(data)
