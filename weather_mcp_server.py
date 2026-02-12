"""
Weather MCP Server - Connects to real weather APIs (OpenWeatherMap)
Provides real-time weather data for the Weather Agent
Falls back to mock data if API key not available
"""

import json
import sys
import os
import random
from datetime import datetime, timedelta

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("WARNING: requests library not installed. Install with: pip install requests", file=sys.stderr)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    def load_dotenv():
        pass
    load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org"
FALLBACK_MODE = not OPENWEATHER_API_KEY or not HAS_REQUESTS

# Fallback mock weather data
MOCK_WEATHER_DATA = {
    "dunedin, fl": {"location": "Dunedin, FL USA", "temperature": 21.1, "feels_like": 20.5, "humidity": 65, "wind_speed": 12.9, "condition": "Sunny", "description": "Sunny skies"},
    "washington dc": {"location": "Washington DC, USA", "temperature": 9.4, "feels_like": 8.0, "humidity": 60, "wind_speed": 14.5, "condition": "Partly Cloudy", "description": "Mix of clouds"},
    "london": {"location": "London, UK", "temperature": 12.5, "feels_like": 11.2, "humidity": 72, "wind_speed": 15.3, "condition": "Partly Cloudy", "description": "Partly cloudy"},
}


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32


def get_fallback_weather(location: str, units: str = "metric") -> dict:
    """Get fallback mock weather data"""
    loc_key = location.lower().replace(" ", "").replace(",", "")
    
    # Try exact match first
    for key, value in MOCK_WEATHER_DATA.items():
        if key.replace(" ", "").replace(",", "") == loc_key:
            weather = value.copy()
            break
    else:
        # Return generic data for unknown location (realistic for Florida)
        weather = {"location": location, "temperature": 21.1, "feels_like": 20.5, "humidity": 65, "wind_speed": 12.9, "condition": "Sunny", "description": "Sunny skies with pleasant weather"}
    
    # Convert units if needed
    if units == "imperial":
        weather["temperature"] = celsius_to_fahrenheit(weather["temperature"])
        weather["feels_like"] = celsius_to_fahrenheit(weather["feels_like"])
        weather["wind_speed"] = weather["wind_speed"] * 0.621371  # km/h to mph
    elif units == "standard":
        weather["temperature"] = weather["temperature"] + 273.15  # Celsius to Kelvin
        weather["feels_like"] = weather["feels_like"] + 273.15
        weather["wind_speed"] = weather["wind_speed"] / 3.6  # km/h to m/s
    
    return weather


def get_current_weather(location: str, units: str = "metric") -> dict:
    """Get current weather from OpenWeatherMap API or fallback to mock data"""
    
    # Use fallback if API key not set or requests not available
    if FALLBACK_MODE:
        weather = get_fallback_weather(location, units)
        weather["timestamp"] = datetime.now().isoformat()
        return weather
    
    if not HAS_REQUESTS:
        return {"error": "requests library not installed. Install with: pip install requests"}
    
    try:
        # Current weather endpoint
        url = f"{OPENWEATHER_BASE_URL}/data/2.5/weather"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "location": f"{data['name']}, {data['sys'].get('country', '')}",
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "pressure": data["main"]["pressure"],
            "cloudiness": data["clouds"]["all"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Fall back to mock data on error
        weather = get_fallback_weather(location)
        weather["timestamp"] = datetime.now().isoformat()
        return weather


def get_forecast(location: str, days: int = 5, units: str = "metric") -> list:
    """Get weather forecast or fallback to mock data"""
    
    # Use fallback if API key not set or requests not available
    if FALLBACK_MODE:
        # Derive forecast from the fallback current weather so units and
        # magnitudes match what `get_current_weather` returns for the
        # requested `units` (avoids fixed 20/15C values that confuse users).
        base = get_fallback_weather(location, units)
        base_temp = base.get("temperature", 20)
        base_wind = base.get("wind_speed", 10)

        forecast_data = []
        for i in range(min(days, 3)):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            temp_max = base_temp + random.uniform(-3, 5)
            temp_min = base_temp - random.uniform(2, 8)
            wind = max(0.0, base_wind + random.uniform(-3, 7))

            forecast_data.append({
                "date": date,
                "condition": "Sunny",
                "temp_max": temp_max,
                "temp_min": temp_min,
                "wind_speed": wind,
            })

        return forecast_data
    
    if not HAS_REQUESTS:
        return []
    
    try:
        # 5-day forecast endpoint
        url = f"{OPENWEATHER_BASE_URL}/data/2.5/forecast"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        forecast_list = data["list"]
        
        # Group by day and get daily forecast
        daily_forecast = {}
        for item in forecast_list:
            date = item["dt_txt"].split(" ")[0]
            if date not in daily_forecast:
                daily_forecast[date] = item
        
        result = []
        for date, item in daily_forecast.items():
            result.append({
                "date": date,
                "temp_max": item["main"]["temp_max"],
                "temp_min": item["main"]["temp_min"],
                "condition": item["weather"][0]["main"],
                "description": item["weather"][0]["description"],
                "precipitation": item.get("rain", {}).get("3h", 0),
                "wind_speed": item["wind"]["speed"],
                "humidity": item["main"]["humidity"]
            })
        
        return result[:days]
    except Exception as e:
        # Fall back to mock data
        return [
            {"date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"), 
             "condition": "Cloudy", "temp_max": 18, "temp_min": 12, "wind_speed": 8}
            for i in range(min(days, 3))
        ]


def get_alerts(location: str) -> list:
    """Get weather alerts or return empty list for fallback"""
    
    if FALLBACK_MODE or not HAS_REQUESTS:
        return []  # No alerts in fallback mode
    
    try:
        # First get coordinates
        url = f"{OPENWEATHER_BASE_URL}/geo/1.0/direct"
        params = {"q": location, "appid": OPENWEATHER_API_KEY}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if not data:
            return []
        
        lat, lon = data[0]["lat"], data[0]["lon"]
        
        # Get alerts
        alerts_url = f"{OPENWEATHER_BASE_URL}/data/3.0/alerts"
        params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}
        
        response = requests.get(alerts_url, params=params, timeout=10)
        response.raise_for_status()
        
        alerts_data = response.json()
        
        alerts = []
        for alert in alerts_data.get("alerts", []):
            alerts.append({
                "title": alert.get("event", "Unknown Alert"),
                "severity": "High",
                "description": alert.get("description", ""),
                "effective_from": alert.get("start", datetime.now().isoformat()),
                "expires": alert.get("end", (datetime.now() + timedelta(hours=6)).isoformat())
            })
        
        return alerts
    except Exception as e:
        return []


def get_air_quality(location: str) -> dict:
    """Get air quality information or fallback data"""
    
    # Return fallback data if not using real API
    if FALLBACK_MODE or not HAS_REQUESTS:
        return {
            "location": location,
            "aqi": 2,
            "aqi_quality": "Fair",
            "pm25": 35.0,
            "pm10": 50.0,
            "no2": 20.0,
            "so2": 10.0,
            "o3": 60.0,
            "co": 0.5,
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # First get coordinates
        url = f"{OPENWEATHER_BASE_URL}/geo/1.0/direct"
        params = {"q": location, "appid": OPENWEATHER_API_KEY}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if not data:
            return {"location": location, "error": "Location not found"}
        
        lat, lon = data[0]["lat"], data[0]["lon"]
        
        # Get air quality
        aqi_url = f"{OPENWEATHER_BASE_URL}/data/3.0/air_pollution"
        params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}
        
        response = requests.get(aqi_url, params=params, timeout=10)
        response.raise_for_status()
        
        aqi_data = response.json()
        main = aqi_data["list"][0]["main"]
        components = aqi_data["list"][0]["components"]
        
        # Convert AQI level to text
        aqi_level = main["aqi"]
        quality_map = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        
        return {
            "location": location,
            "aqi": aqi_level,
            "aqi_quality": quality_map.get(aqi_level, "Unknown"),
            "pm25": components.get("pm2_5", 0),
            "pm10": components.get("pm10", 0),
            "no2": components.get("no2", 0),
            "so2": components.get("so2", 0),
            "o3": components.get("o3", 0),
            "co": components.get("co", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Return fallback on error
        return {
            "location": location,
            "aqi": 2,
            "aqi_quality": "Fair",
            "pm25": 35.0,
            "pm10": 50.0,
            "no2": 20.0,
            "so2": 10.0,
            "o3": 60.0,
            "co": 0.5,
            "timestamp": datetime.now().isoformat()
        }


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Handle tool calls from the MCP client"""
    
    try:
        if tool_name == "get_current_weather":
            location = arguments.get("location", "London")
            units = arguments.get("units", "metric")
            result = get_current_weather(location, units)
            return result
        
        elif tool_name == "get_forecast":
            location = arguments.get("location", "London")
            days = arguments.get("days", 5)
            units = arguments.get("units", "metric")
            result = get_forecast(location, days, units)
            return result if result else {"error": "No forecast data available"}
        
        elif tool_name == "get_alerts":
            location = arguments.get("location", "London")
            result = get_alerts(location)
            return result
        
        elif tool_name == "get_air_quality":
            location = arguments.get("location", "London")
            result = get_air_quality(location)
            return result
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        return {"error": str(e)}


def list_tools() -> list:
    """List available tools"""
    return [
        {
            "name": "get_current_weather",
            "description": "Get current weather conditions for a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_forecast",
            "description": "Get weather forecast for multiple days",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "days": {"type": "integer", "default": 5}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_alerts",
            "description": "Get weather alerts for a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_air_quality",
            "description": "Get air quality information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    ]


def main():
    """Main server loop - reads JSON-RPC requests and sends responses"""
    if FALLBACK_MODE:
        print("Weather MCP Server (FALLBACK MODE - using mock data)", file=sys.stderr)
        if not HAS_REQUESTS:
            print("  Reason: requests library not installed", file=sys.stderr)
        if not OPENWEATHER_API_KEY:
            print("  Reason: OPENWEATHER_API_KEY not set in .env", file=sys.stderr)
        print("  To use real weather: pip install requests && set OPENWEATHER_API_KEY in .env", file=sys.stderr)
    else:
        print("Real-time Weather MCP Server started", file=sys.stderr)
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id", 1)
            
            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = handle_tool_call(tool_name, arguments)
            elif method == "tools/list":
                result = {"tools": list_tools()}
            else:
                result = {"error": f"Unknown method: {method}"}
            
            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
            print(json.dumps(response))
            sys.stdout.flush()
        
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": None
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
