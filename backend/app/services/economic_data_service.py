"""
Economic Data Service
Integrates FRED, World Bank, and IMF APIs for economic indicators
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EconomicDataService:
    def __init__(self):
        self.fred_api_key = settings.fred_api_key
        self.world_bank_api_key = settings.world_bank_api_key
        self.imf_api_key = settings.imf_api_key
        
        self.fred_base_url = "https://api.stlouisfed.org/fred"
        self.world_bank_base_url = settings.world_bank_base_url
        self.imf_base_url = settings.imf_base_url

    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get comprehensive economic indicators"""
        indicators = {}
        
        # Get FRED data
        try:
            fred_data = await self._get_fred_data()
            indicators.update(fred_data)
        except Exception as e:
            logger.warning(f"Failed to fetch FRED data: {e}")
        
        # Get World Bank data
        try:
            world_bank_data = await self._get_world_bank_data()
            indicators.update(world_bank_data)
        except Exception as e:
            logger.warning(f"Failed to fetch World Bank data: {e}")
        
        # Get IMF data
        try:
            imf_data = await self._get_imf_data()
            indicators.update(imf_data)
        except Exception as e:
            logger.warning(f"Failed to fetch IMF data: {e}")
        
        return {
            "indicators": indicators,
            "timestamp": datetime.now().isoformat(),
            "sources": ["fred", "world_bank", "imf"]
        }

    async def _get_fred_data(self) -> Dict[str, Any]:
        """Fetch data from FRED API"""
        if not self.fred_api_key:
            raise Exception("FRED API key not configured")
        
        # Key economic indicators
        series_ids = [
            "GDP",           # Gross Domestic Product
            "UNRATE",        # Unemployment Rate
            "CPIAUCSL",      # Consumer Price Index
            "FEDFUNDS",     # Federal Funds Rate
            "DGS10",         # 10-Year Treasury Rate
            "DEXUSEU",       # USD/EUR Exchange Rate
            "VIXCLS"         # VIX Volatility Index
        ]
        
        fred_data = {}
        
        async with httpx.AsyncClient() as client:
            for series_id in series_ids:
                try:
                    response = await client.get(
                        f"{self.fred_base_url}/series/observations",
                        params={
                            "series_id": series_id,
                            "api_key": self.fred_api_key,
                            "file_type": "json",
                            "limit": 1,
                            "sort_order": "desc"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        observations = data.get("observations", [])
                        if observations:
                            latest = observations[0]
                            fred_data[series_id] = {
                                "value": latest.get("value"),
                                "date": latest.get("date"),
                                "title": self._get_fred_series_title(series_id)
                            }
                except Exception as e:
                    logger.warning(f"Failed to fetch FRED series {series_id}: {e}")
        
        return {"fred": fred_data}

    async def _get_world_bank_data(self) -> Dict[str, Any]:
        """Fetch data from World Bank API"""
        if not self.world_bank_api_key:
            raise Exception("World Bank API key not configured")
        
        # Key World Bank indicators
        indicators = [
            "NY.GDP.MKTP.CD",    # GDP (current US$)
            "FP.CPI.TOTL.ZG",    # Inflation, consumer prices
            "SL.UEM.TOTL.ZS",    # Unemployment, total
            "FR.INR.RINR"        # Real interest rate
        ]
        
        world_bank_data = {}
        
        async with httpx.AsyncClient() as client:
            for indicator in indicators:
                try:
                    response = await client.get(
                        f"{self.world_bank_base_url}/country/USA/indicator/{indicator}",
                        params={
                            "format": "json",
                            "per_page": 1,
                            "date": "2023:2024"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 1:
                            indicator_data = data[1]
                            if indicator_data:
                                latest = indicator_data[0]
                                world_bank_data[indicator] = {
                                    "value": latest.get("value"),
                                    "date": latest.get("date"),
                                    "country": latest.get("country", {}).get("value", "USA")
                                }
                except Exception as e:
                    logger.warning(f"Failed to fetch World Bank indicator {indicator}: {e}")
        
        return {"world_bank": world_bank_data}

    async def _get_imf_data(self) -> Dict[str, Any]:
        """Fetch data from IMF API"""
        if not self.imf_api_key:
            raise Exception("IMF API key not configured")
        
        # This is a simplified implementation
        # IMF API structure is complex and would need specific dataset queries
        return {"imf": {"note": "IMF API integration requires specific dataset configuration"}}

    def _get_fred_series_title(self, series_id: str) -> str:
        """Get human-readable title for FRED series"""
        titles = {
            "GDP": "Gross Domestic Product",
            "UNRATE": "Unemployment Rate",
            "CPIAUCSL": "Consumer Price Index",
            "FEDFUNDS": "Federal Funds Rate",
            "DGS10": "10-Year Treasury Rate",
            "DEXUSEU": "USD/EUR Exchange Rate",
            "VIXCLS": "VIX Volatility Index"
        }
        return titles.get(series_id, series_id)
