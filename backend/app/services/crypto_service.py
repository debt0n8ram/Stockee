"""
Comprehensive Crypto Service with Multiple API Integration
Supports CoinGecko, CoinMarketCap, and CryptoCompare APIs with intelligent fallback
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self):
        self.coingecko_base_url = settings.coingecko_base_url
        self.coinmarketcap_base_url = settings.coinmarketcap_base_url
        self.cryptocompare_base_url = settings.cryptocompare_base_url
        
        # API Keys
        self.coingecko_api_key = settings.coingecko_api_key
        self.coinmarketcap_api_key = settings.coinmarketcap_api_key
        self.cryptocompare_api_key = settings.cryptocompare_api_key
        self.coinapi_api_key = settings.coinapi_api_key
        
        # Rate limiting
        self.coingecko_rate_limit = settings.coingecko_rate_limit
        self.coinmarketcap_rate_limit = settings.coinmarketcap_rate_limit
        self.cryptocompare_rate_limit = settings.cryptocompare_rate_limit
        
        # Symbol mapping for different APIs
        self.symbol_mapping = {
            'BTC': {'coingecko': 'bitcoin', 'coinmarketcap': 'BTC', 'cryptocompare': 'BTC'},
            'ETH': {'coingecko': 'ethereum', 'coinmarketcap': 'ETH', 'cryptocompare': 'ETH'},
            'USDC': {'coingecko': 'usd-coin', 'coinmarketcap': 'USDC', 'cryptocompare': 'USDC'},
            'USDT': {'coingecko': 'tether', 'coinmarketcap': 'USDT', 'cryptocompare': 'USDT'},
            'BNB': {'coingecko': 'binancecoin', 'coinmarketcap': 'BNB', 'cryptocompare': 'BNB'},
            'ADA': {'coingecko': 'cardano', 'coinmarketcap': 'ADA', 'cryptocompare': 'ADA'},
            'SOL': {'coingecko': 'solana', 'coinmarketcap': 'SOL', 'cryptocompare': 'SOL'},
            'DOT': {'coingecko': 'polkadot', 'coinmarketcap': 'DOT', 'cryptocompare': 'DOT'},
            'MATIC': {'coingecko': 'matic-network', 'coinmarketcap': 'MATIC', 'cryptocompare': 'MATIC'},
            'AVAX': {'coingecko': 'avalanche-2', 'coinmarketcap': 'AVAX', 'cryptocompare': 'AVAX'},
            'DOGE': {'coingecko': 'dogecoin', 'coinmarketcap': 'DOGE', 'cryptocompare': 'DOGE'},
            'SHIB': {'coingecko': 'shiba-inu', 'coinmarketcap': 'SHIB', 'cryptocompare': 'SHIB'},
            'LINK': {'coingecko': 'chainlink', 'coinmarketcap': 'LINK', 'cryptocompare': 'LINK'},
            'UNI': {'coingecko': 'uniswap', 'coinmarketcap': 'UNI', 'cryptocompare': 'UNI'},
            'LTC': {'coingecko': 'litecoin', 'coinmarketcap': 'LTC', 'cryptocompare': 'LTC'},
        }

    async def get_crypto_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get crypto prices with intelligent API fallback
        Tries APIs in order: CoinGecko -> CoinMarketCap -> CryptoCompare -> Mock
        """
        symbol_list = [s.strip().upper() for s in symbols]
        
        # Try APIs in order of preference
        apis_to_try = [
            ('coingecko', self._get_coingecko_prices),
            ('coinmarketcap', self._get_coinmarketcap_prices),
            ('cryptocompare', self._get_cryptocompare_prices),
        ]
        
        for api_name, api_func in apis_to_try:
            try:
                result = await api_func(symbol_list)
                if result and result.get('prices'):
                    logger.info(f"Successfully fetched prices from {api_name}")
                    return {
                        **result,
                        'source': api_name,
                        'api_status': 'live',
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch from {api_name}: {e}")
                continue
        
        # Fallback to mock data
        logger.warning("All APIs failed, using mock data")
        return self._get_mock_prices(symbol_list)

    async def _get_coingecko_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch prices from CoinGecko API"""
        coin_ids = []
        for symbol in symbols:
            if symbol in self.symbol_mapping:
                coin_ids.append(self.symbol_mapping[symbol]['coingecko'])
            else:
                coin_ids.append(symbol.lower())
        
        coin_ids_str = ','.join(coin_ids)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.coingecko_base_url}/simple/price",
                params={
                    "ids": coin_ids_str,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                
                for i, symbol in enumerate(symbols):
                    coin_id = coin_ids[i]
                    if coin_id in data:
                        coin_data = data[coin_id]
                        prices[symbol] = {
                            "price": coin_data.get("usd", 0),
                            "change_24h": round(coin_data.get("usd_24h_change", 0), 2),
                            "volume_24h": coin_data.get("usd_24h_vol", 0)
                        }
                
                return {"prices": prices}

    async def _get_coinmarketcap_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch prices from CoinMarketCap API"""
        if not self.coinmarketcap_api_key:
            raise Exception("CoinMarketCap API key not configured")
        
        symbol_str = ','.join(symbols)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.coinmarketcap_base_url}/cryptocurrency/quotes/latest",
                params={"symbol": symbol_str},
                headers={
                    "X-CMC_PRO_API_KEY": self.coinmarketcap_api_key,
                    "Accept": "application/json"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                
                for symbol_data in data.get("data", {}).values():
                    symbol = symbol_data.get("symbol")
                    quote = symbol_data.get("quote", {}).get("USD", {})
                    
                    if symbol in symbols:
                        prices[symbol] = {
                            "price": quote.get("price", 0),
                            "change_24h": round(quote.get("percent_change_24h", 0), 2),
                            "volume_24h": quote.get("volume_24h", 0)
                        }
                
                return {"prices": prices}

    async def _get_cryptocompare_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch prices from CryptoCompare API"""
        symbol_str = ','.join(symbols)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.cryptocompare_base_url}/pricemultifull",
                params={
                    "fsyms": symbol_str,
                    "tsyms": "USD"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                
                raw_data = data.get("RAW", {})
                for symbol in symbols:
                    if symbol in raw_data:
                        symbol_data = raw_data[symbol].get("USD", {})
                        prices[symbol] = {
                            "price": symbol_data.get("PRICE", 0),
                            "change_24h": round(symbol_data.get("CHANGEPCT24HOUR", 0), 2),
                            "volume_24h": symbol_data.get("TOTALVOLUME24H", 0)
                        }
                
                return {"prices": prices}

    def _get_mock_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Fallback mock prices"""
        mock_prices = {
            "BTC": {"price": 45000.0, "change_24h": 2.5, "volume_24h": 25000000000},
            "ETH": {"price": 3200.0, "change_24h": 1.8, "volume_24h": 15000000000},
            "USDC": {"price": 1.0, "change_24h": 0.0, "volume_24h": 5000000000},
            "USDT": {"price": 1.0, "change_24h": 0.0, "volume_24h": 8000000000},
            "BNB": {"price": 320.0, "change_24h": 3.2, "volume_24h": 2000000000},
            "ADA": {"price": 0.45, "change_24h": -1.2, "volume_24h": 800000000},
            "SOL": {"price": 95.0, "change_24h": 4.1, "volume_24h": 1200000000},
            "DOT": {"price": 6.8, "change_24h": 2.1, "volume_24h": 600000000},
            "MATIC": {"price": 0.85, "change_24h": 1.5, "volume_24h": 400000000},
            "AVAX": {"price": 25.0, "change_24h": 2.8, "volume_24h": 700000000}
        }
        
        result = {}
        for symbol in symbols:
            if symbol in mock_prices:
                result[symbol] = mock_prices[symbol]
            else:
                import random
                result[symbol] = {
                    "price": round(random.uniform(0.01, 1000.0), 2),
                    "change_24h": round(random.uniform(-10.0, 10.0), 2),
                    "volume_24h": random.randint(1000000, 1000000000)
                }
        
        return {
            "prices": result,
            "source": "mock",
            "api_status": "fallback"
        }

    async def get_trending_crypto(self) -> Dict[str, Any]:
        """Get trending cryptocurrencies with API fallback"""
        apis_to_try = [
            ('coingecko', self._get_coingecko_trending),
            ('coinmarketcap', self._get_coinmarketcap_trending),
        ]
        
        for api_name, api_func in apis_to_try:
            try:
                result = await api_func()
                if result and result.get('trending'):
                    logger.info(f"Successfully fetched trending from {api_name}")
                    return {
                        **result,
                        'source': api_name,
                        'timestamp': datetime.now().isoformat()
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch trending from {api_name}: {e}")
                continue
        
        # Fallback trending data
        return {
            "trending": [
                {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC", "market_cap_rank": 1},
                {"id": "ethereum", "name": "Ethereum", "symbol": "ETH", "market_cap_rank": 2},
                {"id": "solana", "name": "Solana", "symbol": "SOL", "market_cap_rank": 5},
                {"id": "cardano", "name": "Cardano", "symbol": "ADA", "market_cap_rank": 8},
                {"id": "dogecoin", "name": "Dogecoin", "symbol": "DOGE", "market_cap_rank": 10}
            ],
            "source": "mock",
            "timestamp": datetime.now().isoformat()
        }

    async def _get_coingecko_trending(self) -> Dict[str, Any]:
        """Get trending from CoinGecko"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.coingecko_base_url}/search/trending",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                trending = []
                
                for coin in data.get("coins", [])[:10]:
                    coin_data = coin.get("item", {})
                    trending.append({
                        "id": coin_data.get("id"),
                        "name": coin_data.get("name"),
                        "symbol": coin_data.get("symbol", "").upper(),
                        "market_cap_rank": coin_data.get("market_cap_rank"),
                        "thumb": coin_data.get("thumb")
                    })
                
                return {"trending": trending}

    async def _get_coinmarketcap_trending(self) -> Dict[str, Any]:
        """Get trending from CoinMarketCap"""
        if not self.coinmarketcap_api_key:
            raise Exception("CoinMarketCap API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.coinmarketcap_base_url}/cryptocurrency/trending/most-visited",
                headers={
                    "X-CMC_PRO_API_KEY": self.coinmarketcap_api_key,
                    "Accept": "application/json"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                trending = []
                
                for coin_data in data.get("data", [])[:10]:
                    trending.append({
                        "id": coin_data.get("id"),
                        "name": coin_data.get("name"),
                        "symbol": coin_data.get("symbol"),
                        "market_cap_rank": coin_data.get("cmc_rank"),
                        "thumb": f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin_data.get('id')}.png"
                    })
                
                return {"trending": trending}

    async def get_crypto_news(self, limit: int = 10) -> Dict[str, Any]:
        """Get crypto news from multiple sources"""
        apis_to_try = [
            ('cryptocompare', self._get_cryptocompare_news),
            ('coindesk', self._get_coindesk_news),
        ]
        
        all_news = []
        
        for api_name, api_func in apis_to_try:
            try:
                result = await api_func(limit)
                if result and result.get('news'):
                    for news_item in result['news']:
                        news_item['source_api'] = api_name
                    all_news.extend(result['news'])
            except Exception as e:
                logger.warning(f"Failed to fetch news from {api_name}: {e}")
                continue
        
        # Sort by date and limit
        all_news.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return {
            "news": all_news[:limit],
            "total_sources": len(apis_to_try),
            "timestamp": datetime.now().isoformat()
        }

    async def _get_cryptocompare_news(self, limit: int) -> Dict[str, Any]:
        """Get news from CryptoCompare"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.cryptocompare_base_url}/v2/news/",
                params={"lang": "EN", "sortOrder": "latest"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                news = []
                
                for item in data.get("Data", [])[:limit]:
                    news.append({
                        "title": item.get("title"),
                        "summary": item.get("body"),
                        "url": item.get("url"),
                        "published_at": item.get("published_on"),
                        "source": item.get("source"),
                        "tags": item.get("tags", "").split("|") if item.get("tags") else []
                    })
                
                return {"news": news}

    async def _get_coindesk_news(self, limit: int) -> Dict[str, Any]:
        """Get news from CoinDesk (if API available)"""
        # CoinDesk doesn't have a public API, so this would be a placeholder
        # In practice, you might use RSS feeds or web scraping
        return {"news": []}

    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview"""
        try:
            # Get global market data from CoinGecko
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.coingecko_base_url}/global",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    global_data = data.get("data", {})
                    
                    return {
                        "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                        "total_volume": global_data.get("total_volume", {}).get("usd", 0),
                        "bitcoin_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
                        "ethereum_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0),
                        "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                        "markets": global_data.get("markets", 0),
                        "source": "coingecko",
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            logger.warning(f"Failed to fetch market overview: {e}")
        
        # Fallback data
        return {
            "total_market_cap": 2500000000000,
            "total_volume": 100000000000,
            "bitcoin_dominance": 45.0,
            "ethereum_dominance": 18.0,
            "active_cryptocurrencies": 10000,
            "markets": 500,
            "source": "mock",
            "timestamp": datetime.now().isoformat()
        }
