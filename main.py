"""
Main entry point for the Weather Agent application
"""

import logging
import logging.config
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.weather_agent import WeatherAgent
from src.mcp_client import WeatherMCPClient
from config.config import MCP_SERVER_CONFIG, LOGGING_CONFIG, WEATHER_AGENT_CONFIG


def setup_logging():
    """Configure logging based on configuration"""
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger(__name__)


def main():
    """Main function to run the Weather Agent"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Weather Agent Starting")
    logger.info("=" * 60)

    try:
        # Initialize MCP Client
        mcp_client = WeatherMCPClient(
            server_command=MCP_SERVER_CONFIG["command"],
            server_args=MCP_SERVER_CONFIG["args"]
        )

        # Initialize Weather Agent
        agent = WeatherAgent(mcp_client)

        # Start the agent
        if not agent.start():
            logger.error("Failed to start Weather Agent")
            return 1

        # Example usage: Get weather for multiple locations
        locations = ["London", "New York", "Tokyo", "Washington DC"]
        
        for location in locations:
            logger.info(f"\nFetching weather for {location}...")
            
            # Get current weather
            current_weather = agent.get_current_weather(location)
            if current_weather:
                print(current_weather.to_string())
            
            # Get forecast
            forecast = agent.get_forecast(location, days=5)
            if forecast:
                logger.info(f"Forecast for {location}: {len(forecast)} days")
            
            # Get alerts
            alerts = agent.get_weather_alerts(location)
            if alerts:
                logger.info(f"Weather alerts for {location}: {len(alerts)} alert(s)")
            
            # Get air quality
            air_quality = agent.get_air_quality(location)
            if air_quality:
                logger.info(f"Air quality for {location}: {air_quality}")

        # Comprehensive analysis
        logger.info("\nPerforming comprehensive weather analysis...")
        analysis = agent.analyze_weather("London")
        logger.info(f"Analysis complete: {len(analysis)} metrics gathered")

        # Stop the agent
        agent.stop()
        
        logger.info("=" * 60)
        logger.info("Weather Agent completed successfully")
        logger.info("=" * 60)
        return 0

    except KeyboardInterrupt:
        logger.warning("Weather Agent interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error in Weather Agent: {str(e)}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        logger.warning("Application interrupted")
        exit_code = 1
    except Exception as e:
        logger.exception(f"Fatal error: {str(e)}")
        exit_code = 1
    finally:
        # Ensure clean exit
        import sys
        sys.exit(exit_code)
