"""
Comprehensive Historical Data Service
Integrates multiple APIs for stocks and crypto historical data
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class HistoricalDataService:
    def __init__(self):
        # API Keys
        self.finnhub_api_key = settings.finnhub_api_key
        self.quandl_api_key = settings.quandl_api_key
        self.nasdaq_data_link_api_key = settings.nasdaq_data_link_api_key
        self.coinapi_api_key = settings.coinapi_api_key
        self.coingecko_api_key = settings.coingecko_api_key
        self.cryptocompare_api_key = settings.cryptocompare_api_key
        
        # Base URLs
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        self.quandl_base_url = "https://data.nasdaq.com/api/v3"
        self.coinapi_base_url = settings.coinapi_base_url
        self.coingecko_base_url = settings.coingecko_base_url
        self.cryptocompare_base_url = settings.cryptocompare_base_url

    async def get_stock_historical_data(
        self, 
        symbol: str, 
        days: int = 30,
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get comprehensive stock historical data with multiple API fallback
        """
        symbol = symbol.upper()
        
        # Try APIs in order of preference
        apis_to_try = [
            ('finnhub', self._get_finnhub_stock_data),
            ('quandl', self._get_quandl_stock_data),
            ('nasdaq_data_link', self._get_nasdaq_data_link_stock_data),
        ]
        
        for api_name, api_func in apis_to_try:
            try:
                result = await api_func(symbol, days, interval)
                if result and result.get('data'):
                    logger.info(f"Successfully fetched stock data from {api_name}")
                    return {
                        **result,
                        'source': api_name,
                        'api_status': 'live',
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch stock data from {api_name}: {e}")
                continue
        
        # Fallback to mock data
        logger.warning("All stock APIs failed, using mock data")
        return self._get_mock_stock_data(symbol, days)

    async def get_crypto_historical_data(
        self, 
        symbol: str, 
        days: int = 30,
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get comprehensive crypto historical data with multiple API fallback
        """
        symbol = symbol.upper()
        
        # Try APIs in order of preference
        apis_to_try = [
            ('coinapi', self._get_coinapi_crypto_data),
            ('coingecko', self._get_coingecko_crypto_data),
            ('cryptocompare', self._get_cryptocompare_crypto_data),
        ]
        
        for api_name, api_func in apis_to_try:
            try:
                result = await api_func(symbol, days, interval)
                if result and result.get('data'):
                    logger.info(f"Successfully fetched crypto data from {api_name}")
                    return {
                        **result,
                        'source': api_name,
                        'api_status': 'live',
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch crypto data from {api_name}: {e}")
                continue
        
        # Fallback to mock data
        logger.warning("All crypto APIs failed, using mock data")
        return self._get_mock_crypto_data(symbol, days)

    async def _get_finnhub_stock_data(self, symbol: str, days: int, interval: str) -> Dict[str, Any]:
        """Fetch stock data from Finnhub API"""
        if not self.finnhub_api_key:
            raise Exception("Finnhub API key not configured")
        
        # Calculate timestamp range
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.finnhub_base_url}/stock/candle",
                params={
                    "symbol": symbol,
                    "resolution": interval,
                    "from": start_time,
                    "to": end_time,
                    "token": self.finnhub_api_key
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("s") == "ok":  # Success status
                    candles = data.get("c", [])  # Close prices
                    highs = data.get("h", [])   # High prices
                    lows = data.get("l", [])     # Low prices
                    opens = data.get("o", [])    # Open prices
                    volumes = data.get("v", [])  # Volumes
                    timestamps = data.get("t", [])  # Timestamps
                    
                    historical_data = []
                    for i in range(len(candles)):
                        historical_data.append({
                            "timestamp": datetime.fromtimestamp(timestamps[i]).isoformat(),
                            "open": opens[i],
                            "high": highs[i],
                            "low": lows[i],
                            "close": candles[i],
                            "volume": volumes[i]
                        })
                    
                    return {
                        "symbol": symbol,
                        "data": historical_data,
                        "interval": interval,
                        "days": days
                    }
                else:
                    raise Exception(f"Finnhub API error: {data.get('s', 'unknown')}")

    async def _get_quandl_stock_data(self, symbol: str, days: int, interval: str) -> Dict[str, Any]:
        """Fetch stock data from Quandl/Nasdaq Data Link API"""
        if not self.quandl_api_key:
            raise Exception("Quandl API key not configured")
        
        # Calculate date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.quandl_base_url}/datasets/WIKI/{symbol}.json",
                params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "api_key": self.quandl_api_key
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                dataset = data.get("dataset", {})
                
                if dataset.get("data"):
                    historical_data = []
                    columns = dataset.get("column_names", [])
                    
                    for row in dataset["data"]:
                        row_dict = dict(zip(columns, row))
                        historical_data.append({
                            "timestamp": row_dict.get("Date", ""),
                            "open": row_dict.get("Open"),
                            "high": row_dict.get("High"),
                            "low": row_dict.get("Low"),
                            "close": row_dict.get("Close"),
                            "volume": row_dict.get("Volume")
                        })
                    
                    return {
                        "symbol": symbol,
                        "data": historical_data,
                        "interval": interval,
                        "days": days
                    }

    async def _get_nasdaq_data_link_stock_data(self, symbol: str, days: int, interval: str) -> Dict[str, Any]:
        """Fetch stock data from Nasdaq Data Link API"""
        if not self.nasdaq_data_link_api_key:
            raise Exception("Nasdaq Data Link API key not configured")
        
        # This would be similar to Quandl but with different endpoints
        # Implementation depends on specific Nasdaq Data Link API structure
        raise Exception("Nasdaq Data Link API not yet implemented")

    async def _get_coinapi_crypto_data(self, symbol: str, days: int, interval: str) -> Dict[str, Any]:
        """Fetch crypto data from CoinAPI"""
        if not self.coinapi_api_key:
            raise Exception("CoinAPI key not configured")
        
        # Map symbol to CoinAPI format
        symbol_mapping = {
            'BTC': 'BTC/USD',
            'ETH': 'ETH/USD',
            'SOL': 'SOL/USD',
            'ADA': 'ADA/USD',
            'MATIC': 'MATIC/USD',
            'AVAX': 'AVAX/USD',
            'DOGE': 'DOGE/USD',
            'SHIB': 'SHIB/USD',
            'LINK': 'LINK/USD',
            'UNI': 'UNI/USD',
            'LTC': 'LTC/USD'
        }
        
        coinapi_symbol = symbol_mapping.get(symbol, f"{symbol}/USD")
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.coinapi_base_url}/ohlcv/{coinapi_symbol}/history",
                params={
                    "period_id": interval.upper(),
                    "time_start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "time_end": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "limit": min(days * 24, 10000)  # CoinAPI limit
                },
                headers={
                    "X-CoinAPI-Key": self.coinapi_api_key
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                historical_data = []
                for item in data:
                    historical_data.append({
                        "timestamp": item.get("time_period_start", ""),
                        "open": item.get("price_open"),
                        "high": item.get("price_high"),
                        "low": item.get("price_low"),
                        "close": item.get("price_close"),
                        "volume": item.get("volume_traded")
                    })
                
                return {
                    "symbol": symbol,
                    "data": historical_data,
                    "interval": interval,
                    "days": days
                }

    async def _get_coingecko_crypto_data(self, symbol: str, days: int, interval: str) -> Dict[str, Any]:
        """Fetch crypto data from CoinGecko API"""
        symbol_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'ADA': 'cardano',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'DOGE': 'dogecoin',
            'SHIB': 'shiba-inu',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'LTC': 'litecoin'
        }
        
        coin_id = symbol_mapping.get(symbol, symbol.lower())
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.coingecko_base_url}/coins/{coin_id}/market_chart",
                params={
                    "vs_currency": "usd",
                    "days": days,
                    "interval": "daily" if interval == "1d" else "hourly"
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                prices = data.get("prices", [])
                volumes = data.get("total_volumes", [])
                
                historical_data = []
                for i in range(len(prices)):
                    timestamp = datetime.fromtimestamp(prices[i][0] / 1000).isoformat()
                    price = prices[i][1]
                    volume = volumes[i][1] if i < len(volumes) else 0
                    
                    # Generate OHLC from price (simplified)
                    historical_data.append({
                        "timestamp": timestamp,
                        "open": price * 0.999,  # Simplified OHLC
                        "high": price * 1.001,
                        "low": price * 0.998,
                        "close": price,
                        "volume": volume
                    })
                
                return {
                    "symbol": symbol,
                    "data": historical_data,
                    "interval": interval,
                    "days": days
                }

    async def _get_cryptocompare_crypto_data(self, symbol: str, days: int, interval: str) -> Dict[str, Any]:
        """Fetch crypto data from CryptoCompare API"""
        # Map interval to CryptoCompare format
        interval_mapping = {
            "1d": "day",
            "1h": "hour",
            "1m": "minute"
        }
        
        crypto_interval = interval_mapping.get(interval, "day")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.cryptocompare_base_url}/v2/histoday",
                params={
                    "fsym": symbol,
                    "tsym": "USD",
                    "limit": days,
                    "aggregate": 1
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("Response") == "Success":
                    historical_data = []
                    for item in data.get("Data", []):
                        historical_data.append({
                            "timestamp": datetime.fromtimestamp(item.get("time", 0)).isoformat(),
                            "open": item.get("open"),
                            "high": item.get("high"),
                            "low": item.get("low"),
                            "close": item.get("close"),
                            "volume": item.get("volumeto")
                        })
                    
                    return {
                        "symbol": symbol,
                        "data": historical_data,
                        "interval": interval,
                        "days": days
                    }

    def _get_mock_stock_data(self, symbol: str, days: int) -> Dict[str, Any]:
        """Fallback mock stock data"""
        import random
        
        base_price = 150.0 if symbol == "AAPL" else 300.0 if symbol == "MSFT" else random.uniform(50.0, 500.0)
        
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            price_change = random.uniform(-0.05, 0.05)
            price = base_price * (1 + price_change * (i / days))
            
            high = price * random.uniform(1.0, 1.03)
            low = price * random.uniform(0.97, 1.0)
            open_price = price * random.uniform(0.98, 1.02)
            close_price = price
            volume = random.randint(1000000, 10000000)
            
            data.append({
                "timestamp": date.isoformat(),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
        
        return {
            "symbol": symbol,
            "data": data,
            "source": "mock",
            "api_status": "fallback"
        }

    def _get_mock_crypto_data(self, symbol: str, days: int) -> Dict[str, Any]:
        """Fallback mock crypto data"""
        import random
        
        base_price = 45000.0 if symbol == "BTC" else 3200.0 if symbol == "ETH" else random.uniform(0.01, 1000.0)
        
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            price_change = random.uniform(-0.1, 0.1)
            price = base_price * (1 + price_change * (i / days))
            
            high = price * random.uniform(1.0, 1.05)
            low = price * random.uniform(0.95, 1.0)
            open_price = price * random.uniform(0.98, 1.02)
            close_price = price
            volume = random.randint(1000000, 10000000)
            
            data.append({
                "timestamp": date.isoformat(),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
        
        return {
            "symbol": symbol,
            "data": data,
            "source": "mock",
            "api_status": "fallback"
        }
