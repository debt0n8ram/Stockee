import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class CryptoDataService:
    """Crypto data service using CoinGecko API (free alternative to Binance)"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit = 10  # requests per minute for free tier
        self.last_request_time = 0
        
    def _rate_limit_check(self):
        """Implement rate limiting"""
        import time
        now = time.time()
        
        # Check rate limit (requests per minute)
        if now - self.last_request_time < 60 / self.rate_limit:
            sleep_time = (60 / self.rate_limit) - (now - self.last_request_time)
            logger.info(f"CoinGecko rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Make API request with rate limiting"""
        self._rate_limit_check()
        
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko API request failed: {e}")
            raise Exception(f"Failed to fetch data from CoinGecko: {e}")
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price for a cryptocurrency"""
        try:
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'LINK': 'chainlink',
                'LTC': 'litecoin',
                'BCH': 'bitcoin-cash',
                'XRP': 'ripple',
                'DOGE': 'dogecoin',
                'SHIB': 'shiba-inu'
            }
            
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            
            data = self._make_request(f"/simple/price", {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            })
            
            if coin_id in data:
                coin_data = data[coin_id]
                return {
                    'symbol': symbol.upper(),
                    'price': coin_data['usd'],
                    'change_24h': coin_data.get('usd_24h_change', 0),
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'last_updated': datetime.fromtimestamp(coin_data.get('last_updated_at', 0)).isoformat(),
                    'source': 'coingecko'
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting crypto price for {symbol}: {e}")
            return None
    
    def get_crypto_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of top cryptocurrencies"""
        try:
            data = self._make_request("/coins/markets", {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': str(limit),
                'page': '1',
                'sparkline': 'false'
            })
            
            cryptos = []
            for coin in data:
                cryptos.append({
                    'symbol': coin['symbol'].upper(),
                    'name': coin['name'],
                    'price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'volume_24h': coin['total_volume'],
                    'change_24h': coin['price_change_percentage_24h'],
                    'rank': coin['market_cap_rank']
                })
            
            return cryptos
            
        except Exception as e:
            logger.error(f"Error getting crypto list: {e}")
            return []
    
    def get_crypto_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical price data for a cryptocurrency"""
        try:
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'LINK': 'chainlink',
                'LTC': 'litecoin',
                'BCH': 'bitcoin-cash',
                'XRP': 'ripple',
                'DOGE': 'dogecoin',
                'SHIB': 'shiba-inu'
            }
            
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            
            data = self._make_request(f"/coins/{coin_id}/market_chart", {
                'vs_currency': 'usd',
                'days': str(days),
                'interval': 'daily' if days > 1 else 'hourly'
            })
            
            if 'prices' in data:
                history = []
                prices = data['prices']
                volumes = data.get('total_volumes', [])
                
                for i, price_point in enumerate(prices):
                    timestamp = datetime.fromtimestamp(price_point[0] / 1000)
                    volume = volumes[i][1] if i < len(volumes) else 0
                    
                    history.append({
                        'timestamp': timestamp.isoformat(),
                        'price': price_point[1],
                        'volume': volume
                    })
                
                return history
            return []
            
        except Exception as e:
            logger.error(f"Error getting crypto history for {symbol}: {e}")
            return []
    
    def search_cryptos(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for cryptocurrencies"""
        try:
            data = self._make_request("/search", {'query': query})
            
            if 'coins' in data:
                results = []
                for coin in data['coins'][:limit]:
                    results.append({
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name'],
                        'id': coin['id'],
                        'market_cap_rank': coin.get('market_cap_rank')
                    })
                return results
            return []
            
        except Exception as e:
            logger.error(f"Error searching cryptos for '{query}': {e}")
            return []
    
    def get_trending_cryptos(self) -> List[Dict[str, Any]]:
        """Get trending cryptocurrencies"""
        try:
            data = self._make_request("/search/trending")
            
            if 'coins' in data:
                trending = []
                for coin_data in data['coins']:
                    coin = coin_data['item']
                    trending.append({
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name'],
                        'id': coin['id'],
                        'market_cap_rank': coin.get('market_cap_rank'),
                        'score': coin_data.get('score', 0)
                    })
                return trending
            return []
            
        except Exception as e:
            logger.error(f"Error getting trending cryptos: {e}")
            return []
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status"""
        return {
            'service': 'CoinGecko',
            'rate_limit_per_minute': self.rate_limit,
            'last_request_time': datetime.fromtimestamp(self.last_request_time).isoformat() if self.last_request_time else None,
            'status': 'active'
        }
