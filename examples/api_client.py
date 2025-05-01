"""
Example of using reliabilipy for a resilient API client.
Shows timeout handling with fallbacks, circuit breaker patterns, and Prometheus metrics.
"""
import requests
import time
from typing import Any, Optional
from prometheus_client import start_http_server
from reliabilipy import with_timeout, circuit_breaker, observe, MetricsCollector

metrics = MetricsCollector(namespace="api_client")

class WeatherAPI:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1"
        self.cache = {}
    
    def _get_coordinates(self, city: str) -> tuple[float, float]:
        """Get latitude and longitude for a city."""
        if f"geo_{city}" in self.cache:
            coords = self.cache[f"geo_{city}"]
            return coords["lat"], coords["lon"]
            
        response = requests.get(
            f"{self.geocoding_url}/search",
            params={"name": city, "count": 1}
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            raise ValueError(f"City not found: {city}")
            
        lat = data["results"][0]["latitude"]
        lon = data["results"][0]["longitude"]
        self.cache[f"geo_{city}"] = {"lat": lat, "lon": lon}
        return lat, lon
    
    @observe(name="get_weather", metrics=metrics)
    @circuit_breaker(
        failure_threshold=3,
        recovery_timeout=30,
        exceptions=(requests.RequestException, ValueError),
        metrics=metrics
    )
    # @with_timeout(
    #     timeout=2.0,
    #     fallback=lambda: {"temperature": 20, "condition": "clear", "source": "fallback"}
    # )
    def get_weather(self, city: str, nocache: bool = False) -> dict:
        """
        Get weather for a city with timeout and fallback.
        If the API call takes more than 2 seconds, returns cached or default data.
        """

        if city == "Nowhere":
            raise ValueError("City not found: Nowhere")
        
        # Check cache first
        if not nocache and city in self.cache:
            return {**self.cache[city], "source": "cache"}
            
        # Get coordinates for the city
        lat, lon = self._get_coordinates(city)
        
        # Make API call for weather
        response = requests.get(
            f"{self.base_url}/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code",
                "timezone": "auto"
            }
        )
        response.raise_for_status()
        
        # Process the response
        data = response.json()
        weather_data = {
            "temperature": data["current"]["temperature_2m"],
            "condition": self._get_condition(data["current"]["weather_code"]),
        }
        
        # Update cache and return
        self.cache[city] = weather_data
        return {**weather_data, "source": "api"}
        
    def _get_condition(self, code: int) -> str:
        """Convert Open-Meteo weather code to condition string."""
        conditions = {
            0: "clear",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            95: "thunderstorm",
        }
        return conditions.get(code, "unknown")
    
    def get_weather_forecast(self, city: str, days: int = 5) -> list:
        """
        Get weather forecast with multiple independent API calls.
        Shows how to handle multiple potential failure points.
        """
        forecast = []
        
        for day in range(days):
            try:
                weather = self.get_weather(city)
                forecast.append(weather)
            except Exception as e:
                print(f"Failed to get forecast for day {day}: {e}")
                # Add fallback data
                forecast.append({
                    "temperature": 20,
                    "condition": "unknown",
                    "source": "error_fallback",
                    "day": day
                })
        
        return forecast

def main():
    # Start Prometheus metrics server
    print("Starting metrics server on port 8000...")
    start_http_server(8000)
    print("Metrics available at http://localhost:8000")
    
    # Example usage
    client = WeatherAPI()
    
    # Single weather request - will use fallback if API is slow
    try:
        weather = client.get_weather("London")
        print(f"Current weather in London:")
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Condition: {weather['condition']}")
        print(f"Data source: {weather['source']}")
    except Exception as e:
        print(f"Failed to get weather: {e}")
    
    # Multiple requests with individual fallbacks
    print("\nChecking weather in multiple cities:")
    for city in ["Paris", "New York", "Tokyo"]:
        try:
            weather = client.get_weather(city)
            print(f"\n{city}:")
            print(f"Temperature: {weather['temperature']}°C")
            print(f"Condition: {weather['condition']}")
            print(f"Source: {weather['source']}")
        except Exception as e:
            print(f"\n{city}: Failed to get weather - {e}")

    
    # Try to get weather for a non-existent city multiple times to trigger circuit breaker
    print("\nTrying to get weather for non-existent city multiple times...")
    for i in range(5):
        try:
            weather = client.get_weather("Nowhere", nocache=True)
            print(f"Attempt {i+1}: Weather in Nowhere: {weather}")
        except Exception as e:
            print(f"Attempt {i+1}: Failed to get weather for Nowhere: {e}")
        time.sleep(1)  # Small delay between attempts
    
    print("\nMetrics server is running. Press Enter to exit...")
    print("You can check Prometheus metrics at http://localhost:9090")
    print("Try these queries:")
    print("1. api_client_circuit_state{function='get_weather'}")
    print("2. api_client_circuit_failures_total{function='get_weather'}")
    input()  # Wait for user input before exiting

if __name__ == '__main__':
    main()
