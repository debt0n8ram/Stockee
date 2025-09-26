"""
Weather and Commodities Service
Integrates OpenWeatherMap API for weather-based trading insights
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class WeatherCommoditiesService:
    def __init__(self):
        self.openweather_api_key = settings.openweather_api_key
        self.openweather_base_url = "https://api.openweathermap.org/data/2.5"

    async def get_weather_commodity_insights(self) -> Dict[str, Any]:
        """Get weather data that affects commodity prices"""
        insights = {}
        
        # Key locations for commodity trading
        locations = {
            "agricultural": [
                {"name": "Chicago", "lat": 41.8781, "lon": -87.6298, "commodity": "corn"},
                {"name": "Kansas City", "lat": 39.0997, "lon": -94.5786, "commodity": "wheat"},
                {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "commodity": "oil"}
            ],
            "energy": [
                {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "commodity": "oil"},
                {"name": "New York", "lat": 40.7128, "lon": -74.0060, "commodity": "natural_gas"}
            ]
        }
        
        for category, location_list in locations.items():
            category_insights = []
            
            for location in location_list:
                try:
                    weather_data = await self._get_weather_data(location["lat"], location["lon"])
                    commodity_impact = self._analyze_commodity_impact(weather_data, location["commodity"])
                    
                    category_insights.append({
                        "location": location["name"],
                        "commodity": location["commodity"],
                        "weather": weather_data,
                        "impact": commodity_impact
                    })
                except Exception as e:
                    logger.warning(f"Failed to get weather data for {location['name']}: {e}")
            
            insights[category] = category_insights
        
        return {
            "weather_commodity_insights": insights,
            "timestamp": datetime.now().isoformat()
        }

    async def _get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API"""
        if not self.openweather_api_key:
            raise Exception("OpenWeatherMap API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.openweather_base_url}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.openweather_api_key,
                    "units": "metric"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "temperature": data.get("main", {}).get("temp"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "pressure": data.get("main", {}).get("pressure"),
                    "weather_condition": data.get("weather", [{}])[0].get("main"),
                    "weather_description": data.get("weather", [{}])[0].get("description"),
                    "wind_speed": data.get("wind", {}).get("speed"),
                    "wind_direction": data.get("wind", {}).get("deg"),
                    "visibility": data.get("visibility"),
                    "cloudiness": data.get("clouds", {}).get("all")
                }

    def _analyze_commodity_impact(self, weather_data: Dict[str, Any], commodity: str) -> Dict[str, Any]:
        """Analyze how weather affects commodity prices"""
        temperature = weather_data.get("temperature", 20)
        humidity = weather_data.get("humidity", 50)
        weather_condition = weather_data.get("weather_condition", "Clear")
        wind_speed = weather_data.get("wind_speed", 0)
        
        impact_score = 0.5  # Neutral
        impact_factors = []
        
        if commodity == "corn":
            # Corn is sensitive to temperature and precipitation
            if temperature > 30:  # Hot weather
                impact_score += 0.2
                impact_factors.append("High temperature may stress crops")
            elif temperature < 10:  # Cold weather
                impact_score -= 0.1
                impact_factors.append("Cold weather may delay planting")
            
            if weather_condition in ["Rain", "Thunderstorm"]:
                impact_score += 0.1
                impact_factors.append("Rain benefits crop growth")
            elif weather_condition in ["Clear", "Sunny"]:
                if humidity < 30:
                    impact_score -= 0.1
                    impact_factors.append("Dry conditions may stress crops")
        
        elif commodity == "wheat":
            # Wheat is sensitive to temperature and moisture
            if temperature > 25:
                impact_score += 0.15
                impact_factors.append("Warm weather accelerates growth")
            
            if weather_condition in ["Rain", "Thunderstorm"]:
                impact_score += 0.05
                impact_factors.append("Moisture benefits wheat crops")
        
        elif commodity == "oil":
            # Oil is affected by weather events that impact production/transport
            if weather_condition in ["Thunderstorm", "Snow"]:
                impact_score += 0.1
                impact_factors.append("Severe weather may disrupt oil operations")
            
            if wind_speed > 15:  # High winds
                impact_score += 0.05
                impact_factors.append("High winds may affect offshore operations")
        
        elif commodity == "natural_gas":
            # Natural gas demand is weather-dependent
            if temperature < 0:  # Very cold
                impact_score += 0.2
                impact_factors.append("Cold weather increases heating demand")
            elif temperature > 25:  # Hot weather
                impact_score += 0.1
                impact_factors.append("Hot weather increases cooling demand")
        
        # Normalize impact score
        impact_score = max(0, min(1, impact_score))
        
        return {
            "impact_score": round(impact_score, 2),
            "impact_level": "high" if impact_score > 0.7 else "medium" if impact_score > 0.4 else "low",
            "impact_factors": impact_factors,
            "trading_recommendation": self._get_trading_recommendation(impact_score, commodity)
        }

    def _get_trading_recommendation(self, impact_score: float, commodity: str) -> str:
        """Get trading recommendation based on weather impact"""
        if impact_score > 0.7:
            return f"Consider bullish positions on {commodity} - weather conditions favor price increases"
        elif impact_score < 0.3:
            return f"Consider bearish positions on {commodity} - weather conditions may pressure prices"
        else:
            return f"Neutral outlook for {commodity} - weather impact is moderate"

    async def get_historical_weather_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get historical weather data for backtesting weather-based strategies"""
        # This would integrate with historical weather APIs
        # For now, return mock data structure
        return {
            "historical_weather": [],
            "note": "Historical weather analysis requires additional weather data APIs",
            "timestamp": datetime.now().isoformat()
        }
