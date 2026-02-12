# Weather Agent - MCP Server Integration

A sophisticated Python-based weather agent that connects with a Weather Model Context Protocol (MCP) server to provide real-time weather updates, forecasts, alerts, and air quality information.

## Features

🌤️ **Current Weather**
- Real-time weather conditions
- Temperature, humidity, wind speed
- Feels-like temperature
- Weather description and conditions

📅 **Weather Forecasts**
- Multi-day weather forecasts (configurable days)
- Temperature trends
- Precipitation predictions
- Severity assessments

⚠️ **Weather Alerts**
- Active weather warnings
- Alert severity levels
- Timely notifications for dangerous conditions
- Location-specific alerts

💨 **Air Quality Monitoring**
- Air Quality Index (AQI)
- PM2.5 and PM10 measurements
- Pollutant concentrations
- Health recommendations

## Architecture

```
Weather Agent
    ├── MCP Client (Communication with MCP Server)
    ├── Weather Agent (Business Logic)
    ├── Configuration Management
    └── Logging & Monitoring
```

## Project Structure

```
.
├── src/
│   ├── __init__.py              # Package initialization
│   ├── mcp_client.py            # MCP Server client
│   └── weather_agent.py         # Main weather agent logic
├── config/
│   ├── __init__.py
│   └── config.py                # Configuration settings
├── tests/
│   └── test_weather_agent.py    # Tests and examples
├── main.py                       # Entry point
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Node.js (if using Node.js-based MCP server)

### Setup Steps

1. **Clone or navigate to the project directory:**
```bash
cd c:\Durgaprasad\AiAdoption
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Copy the example file
copy .env.example .env

# Edit .env with your settings
# OPENWEATHER_API_KEY=your_key_here
# DEFAULT_LOCATION=London
# etc.
```

5. **Install MCP Server (if using Node.js version):**
```bash
npm install -g @modelcontextprotocol/server-weather
```

## Usage

### Quick Start

Run the main application:
```bash
python main.py
```

### Using the Weather Agent in Your Code

```python
from src.weather_agent import WeatherAgent
from src.mcp_client import WeatherMCPClient
from config.config import MCP_SERVER_CONFIG

# Initialize components
mcp_client = WeatherMCPClient(
    server_command=MCP_SERVER_CONFIG["command"],
    server_args=MCP_SERVER_CONFIG["args"]
)
agent = WeatherAgent(mcp_client)

# Start the agent
if agent.start():
    # Get current weather
    weather = agent.get_current_weather("London")
    if weather:
        print(weather.to_string())
    
    # Get forecast
    forecast = agent.get_forecast("London", days=5)
    
    # Get weather alerts
    alerts = agent.get_weather_alerts("London")
    
    # Get air quality
    air_quality = agent.get_air_quality("London")
    
    # Comprehensive analysis
    analysis = agent.analyze_weather("London")
    
    # Stop the agent
    agent.stop()
```

### Running Tests

```bash
python tests/test_weather_agent.py
```

## API Reference

### WeatherAgent Class

#### Methods

- **`start() -> bool`**
  - Initializes and starts the MCP server
  - Returns: True if successful

- **`stop() -> None`**
  - Gracefully stops the MCP server

- **`get_current_weather(location: str) -> Optional[WeatherData]`**
  - Fetches current weather for a location
  - Args: Location name or coordinates
  - Returns: WeatherData object

- **`get_forecast(location: str, days: int = 5) -> Optional[list]`**
  - Gets multi-day weather forecast
  - Args: Location, number of days
  - Returns: List of forecast data

- **`get_weather_alerts(location: str) -> Optional[list]`**
  - Retrieves active weather alerts
  - Args: Location name or coordinates
  - Returns: List of weather alerts

- **`get_air_quality(location: str) -> Optional[Dict[str, Any]]`**
  - Gets air quality information
  - Args: Location name or coordinates
  - Returns: Air quality metrics

- **`analyze_weather(location: str) -> Dict[str, Any]`**
  - Performs comprehensive weather analysis
  - Args: Location name or coordinates
  - Returns: Dictionary with all weather metrics

### WeatherData Class

Data class containing weather information:
- `location`: City name
- `temperature`: Current temperature (°C)
- `feels_like`: Feels-like temperature (°C)
- `humidity`: Humidity percentage (%)
- `wind_speed`: Wind speed (km/h)
- `condition`: Weather condition
- `description`: Detailed description
- `timestamp`: Update timestamp

## Configuration

Edit `config/config.py` to customize:

### MCP Server Configuration
```python
MCP_SERVER_CONFIG = {
    "command": "npx",  # or "python"
    "args": ["@modelcontextprotocol/server-weather"],
    "enabled": True
}
```

### Weather Agent Settings
```python
WEATHER_AGENT_CONFIG = {
    "timeout": 30,              # Request timeout
    "retry_attempts": 3,        # Retry failed requests
    "cache_duration": 600,      # Cache duration (seconds)
    "default_location": "London",
    "units": "metric"           # metric, imperial, standard
}
```

### Feature Flags
```python
FEATURES = {
    "enable_forecast": True,
    "enable_alerts": True,
    "enable_air_quality": True,
    "enable_caching": True,
    "enable_analytics": False
}
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```
MCP_SERVER_ENABLED=true
MCP_SERVER_COMMAND=npx
MCP_SERVER_ARGS=@modelcontextprotocol/server-weather
DEFAULT_LOCATION=London
WEATHER_UNITS=metric
OPENWEATHER_API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

## Logging

Logs are stored in the `logs/` directory automatically. Configure logging in `config/config.py`:

```python
LOGGING_CONFIG = {
    "handlers": {
        "console": {...},  # Console output
        "file": {...}      # File output
    }
}
```

## Troubleshooting

### MCP Server Not Starting
- Ensure Node.js is installed if using Node.js MCP server
- Check MCP_SERVER_COMMAND and MCP_SERVER_ARGS in config
- Verify the server package is installed: `npm install -g @modelcontextprotocol/server-weather`

### Import Errors
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check Python path configuration

### API Key Issues
- Verify OPENWEATHER_API_KEY is set in `.env`
- Ensure the API key is valid and has appropriate permissions
- Check API rate limits

### Connection Timeouts
- Increase timeout in `WEATHER_AGENT_CONFIG["timeout"]`
- Check network connectivity
- Verify MCP server is running

## Advanced Usage

### Async Operations (Future Enhancement)

The agent can be extended for async operations:

```python
# Future implementation
async def get_weather_async(location: str) -> WeatherData:
    # Async implementation
    pass
```

### Caching

Enable caching in configuration to reduce API calls:

```python
FEATURES["enable_caching"] = True
WEATHER_AGENT_CONFIG["cache_duration"] = 600  # 10 minutes
```

### Multiple Locations

Monitor weather for multiple locations:

```python
locations = ["London", "New York", "Tokyo", "Sydney"]
for location in locations:
    weather = agent.get_current_weather(location)
    print(weather.to_string())
```

## Dependencies

- **requests**: HTTP client for API calls
- **python-dotenv**: Environment variable management
- **mcp**: Model Context Protocol library
- **numpy**: Numerical computations (optional)
- **pandas**: Data analysis (optional)

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black src/ config/ tests/

# Lint code
flake8 src/ config/ tests/

# Type checking
mypy src/ config/
```

## License

This project is part of the AI Adoption initiative.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

## Changelog

### Version 1.0.0
- Initial release
- Core weather agent implementation
- MCP server integration
- Basic weather data retrieval
- Forecast, alerts, and air quality features

## Future Enhancements

- [ ] Async/await support
- [ ] Database caching layer
- [ ] REST API wrapper
- [ ] Web dashboard
- [ ] Mobile app integration
- [ ] Machine learning for prediction
- [ ] Real-time data streaming
- [ ] Multi-language support
- [ ] Historical data analysis
- [ ] Custom notifications

## Integration Examples

### With Discord Bot
```python
# Send weather updates to Discord
import discord
weather = agent.get_current_weather("London")
await channel.send(weather.to_string())
```

### With Slack
```python
# Post weather to Slack
from slack_sdk import WebClient
client.chat_postMessage(
    channel="weather",
    text=weather.to_string()
)
```

### With Email Alerts
```python
# Send weather alerts via email
import smtplib
alerts = agent.get_weather_alerts("London")
# Email logic here
```
