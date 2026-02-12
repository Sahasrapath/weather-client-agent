#!/usr/bin/env python
"""
Simple script to get weather for any location
Usage: python get_weather.py "Washington DC"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.weather_agent import WeatherAgent
from src.mcp_client import WeatherMCPClient
from config.config import MCP_SERVER_CONFIG, WEATHER_AGENT_CONFIG

def get_weather(location: str):
    """Get weather for a location and display it"""
    
    # Initialize client and agent
    mcp_client = WeatherMCPClient(
        server_command=MCP_SERVER_CONFIG["command"],
        server_args=MCP_SERVER_CONFIG["args"]
    )
    agent = WeatherAgent(mcp_client)
    
    # Start the agent
    if not agent.start():
        print("Failed to start Weather Agent")
        return
    
    try:
        print(f"\nFetching weather for {location}...\n")
        
        # Get current weather
        weather = agent.get_current_weather(location)
        if weather:
            print(weather.to_string())
        else:
            print(f"Could not fetch weather for {location}")
        
        # Get units from config
        units = WEATHER_AGENT_CONFIG.get("units", "metric")
        if units == "imperial":
            temp_unit = "F"
            wind_unit = "mph"
        elif units == "standard":
            temp_unit = "K"
            wind_unit = "m/s"
        else:
            temp_unit = "C"
            wind_unit = "km/h"
        
        # Get forecast
        forecast = agent.get_forecast(location, days=3)
        if forecast:
            print(f"\n3-Day Forecast for {location}:")
            print("-" * 50)
            for day in forecast:
                print(f"{day['date']}: {day['condition']}")
                temp_max = round(day.get('temp_max', 0), 1) if isinstance(day.get('temp_max'), (int, float)) else 'N/A'
                temp_min = round(day.get('temp_min', 0), 1) if isinstance(day.get('temp_min'), (int, float)) else 'N/A'
                wind = round(day.get('wind_speed', 0), 1) if isinstance(day.get('wind_speed'), (int, float)) else 'N/A'
                print(f"  Temp: {temp_max}{temp_unit} / {temp_min}{temp_unit}")
                print(f"  Wind: {wind} {wind_unit}")
                print()
        
        # Get air quality
        air_quality = agent.get_air_quality(location)
        if air_quality and "error" not in air_quality:
            print(f"\nAir Quality for {location}:")
            print("-" * 50)
            print(f"AQI: {air_quality.get('aqi', 'N/A')} - {air_quality.get('quality', 'N/A')}")
            print(f"PM2.5: {air_quality.get('pm25', 'N/A')} µg/m³")
            print(f"PM10: {air_quality.get('pm10', 'N/A')} µg/m³")
        
    finally:
        agent.stop()

if __name__ == "__main__":
    location = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Washington DC"
    get_weather(location)
