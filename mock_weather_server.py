"""
Mock Weather MCP Server - Simulates a weather service for testing
Provides weather data without needing external dependencies
"""

import json
import sys
from datetime import datetime, timedelta
import random
import os

# Mock weather data for various locations
MOCK_WEATHER_DATA = {
    "london": {
        "location": "London, UK",
        "temperature": 12.5,
        "feels_like": 11.2,
        "humidity": 72,
        "wind_speed": 15.3,
        "condition": "Partly Cloudy",
        "description": "Partly cloudy skies with occasional sun",
    },
    "new york": {
        "location": "New York, USA",
        "temperature": 5.2,
        "feels_like": 2.8,
        "humidity": 65,
        "wind_speed": 18.5,
        "condition": "Cold & Clear",
        "description": "Clear skies with cold temperatures",
    },
    "tokyo": {
        "location": "Tokyo, Japan",
        "temperature": 8.3,
        "feels_like": 6.5,
        "humidity": 58,
        "wind_speed": 12.1,
        "condition": "Overcast",
        "description": "Overcast conditions throughout the day",
    },
    "sydney": {
        "location": "Sydney, Australia",
        "temperature": 26.7,
        "feels_like": 25.1,
        "humidity": 60,
        "wind_speed": 8.5,
        "condition": "Sunny",
        "description": "Sunny and warm with light breeze",
    },
    "dunedin, fl": {
        "location": "Dunedin, FL USA",
        "temperature": 21.1,  # ~70F
        "feels_like": 20.5,
        "humidity": 65,
        "wind_speed": 12.9,
        "condition": "Sunny",
        "description": "Sunny skies with pleasant weather",
    },
    "washington dc": {
        "location": "Washington DC, USA",
        "temperature": 9.4,  # ~49F
        "feels_like": 8.0,
        "humidity": 60,
        "wind_speed": 14.5,
        "condition": "Partly Cloudy",
        "description": "Mix of clouds and sun",
    },
    "los angeles": {
        "location": "Los Angeles, CA USA",
        "temperature": 20.0,  # ~68F
        "feels_like": 19.5,
        "humidity": 55,
        "wind_speed": 10.2,
        "condition": "Sunny",
        "description": "Clear sunny skies",
    },
    "miami": {
        "location": "Miami, FL USA",
        "temperature": 24.4,  # ~76F
        "feels_like": 23.8,
        "humidity": 70,
        "wind_speed": 11.3,
        "condition": "Mostly Sunny",
        "description": "Warm and pleasant weather",
    },
}

def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def get_current_weather(location: str, units: str = "metric") -> dict:
    """Get current weather for a location"""
    loc_key = location.lower()
    
    # Match location or use random data
    if loc_key in MOCK_WEATHER_DATA:
        weather = MOCK_WEATHER_DATA[loc_key].copy()
    else:
        # Generate random weather for unknown locations (more realistic range)
        # Using 10-28C range (50-82F)
        base_temp = random.uniform(10, 28)
        weather = {
            "location": location,
            "temperature": base_temp,
            "feels_like": base_temp - random.uniform(0.5, 2.0),
            "humidity": random.randint(50, 85),
            "wind_speed": random.uniform(5, 20),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Overcast", "Partly Cloudy"]),
            "description": "Weather conditions for the location",
        }
    
    # Convert units if needed
    if units == "imperial":
        weather["temperature"] = celsius_to_fahrenheit(weather["temperature"])
        weather["feels_like"] = celsius_to_fahrenheit(weather["feels_like"])
        weather["wind_speed"] = weather["wind_speed"] * 0.621371  # km/h to mph
    elif units == "standard":
        weather["temperature"] = weather["temperature"] + 273.15  # Celsius to Kelvin
        weather["feels_like"] = weather["feels_like"] + 273.15
        weather["wind_speed"] = weather["wind_speed"] / 3.6  # km/h to m/s
    
    weather["timestamp"] = datetime.now().isoformat()
    return weather


def get_forecast(location: str, days: int = 5, units: str = "metric") -> list:
    """Get weather forecast for a location.

    Forecast values are generated relative to the current conditions and
    returned in the requested `units` so they match the client's expectations.
    """
    forecast = []
    # Request current weather in the desired units so forecast uses same units
    base_weather = get_current_weather(location, units)
    base_temp = base_weather.get("temperature", 0)
    base_wind = base_weather.get("wind_speed", 0)

    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        temp_max = base_temp + random.uniform(-3, 5)
        temp_min = base_temp - random.uniform(2, 8)
        # Wind variation around base_wind (keeps same units as base_weather)
        wind = max(0.0, base_wind + random.uniform(-3, 7))

        forecast.append({
            "date": date,
            "temp_max": temp_max,
            "temp_min": temp_min,
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]),
            "precipitation": random.uniform(0, 30),
            "wind_speed": wind,
        })

    return forecast


def get_alerts(location: str) -> list:
    """Get weather alerts for a location"""
    alerts = []
    
    # Mock alerts based on location
    if random.random() > 0.7:  # 30% chance of alerts
        severity = random.choice(["Low", "Medium", "High"])
        alerts.append({
            "title": f"Weather Alert for {location}",
            "severity": severity,
            "description": f"A {severity.lower()} severity weather alert is in effect.",
            "effective_from": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(hours=6)).isoformat(),
        })
    
    return alerts


def get_air_quality(location: str) -> dict:
    """Get air quality information for a location"""
    return {
        "location": location,
        "aqi": random.randint(20, 150),
        "pm25": random.uniform(5, 100),
        "pm10": random.uniform(10, 150),
        "no2": random.uniform(5, 50),
        "so2": random.uniform(2, 30),
        "o3": random.uniform(20, 150),
        "quality": random.choice(["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy"]),
        "timestamp": datetime.now().isoformat(),
    }


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Handle tool calls from the MCP client"""
    
    # Get units from arguments or environment (default to metric)
    units = arguments.get("units", os.getenv("WEATHER_UNITS", "metric"))
    
    try:
        if tool_name == "get_current_weather":
            location = arguments.get("location", "London")
            result = get_current_weather(location, units)
            return result
        
        elif tool_name == "get_forecast":
            location = arguments.get("location", "London")
            days = arguments.get("days", 5)
            units = arguments.get("units", os.getenv("WEATHER_UNITS", "metric"))
            result = get_forecast(location, days, units)
            return result
        
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
            "description": "Get current weather for a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name or coordinates"}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_forecast",
            "description": "Get weather forecast",
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
            "description": "Get weather alerts",
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
    print("Mock Weather MCP Server started", file=sys.stderr)
    
    while True:
        try:
            # Read request from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id", 1)
            
            # Handle different methods
            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = handle_tool_call(tool_name, arguments)
            elif method == "tools/list":
                result = {"tools": list_tools()}
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Send response
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
