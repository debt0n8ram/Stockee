import requests
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

class PolygonService:
    """Polygon.io API service for additional market data"""
    
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io"
        self.rate_limit = 5  # requests per minute for free tier
        self.last_request_time = 0
        
    def _rate_limit_check(self):
        """Implement rate limiting"""
        now = time.time()
        
        # Check rate limit (requests per minute)
        if now - self.last_request_time < 60 / self.rate_limit:
            sleep_time = (60 / self.rate_limit) - (now - self.last_request_time)
            logger.info(f"Polygon rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Make API request with rate limiting"""
        self._rate_limit_check()
        
        if params is None:
            params = {}
        
        params['apikey'] = self.api_key
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if data.get('status') == 'ERROR':
                raise Exception(f"Polygon API Error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Polygon API request failed: {e}")
            raise Exception(f"Failed to fetch data from Polygon: {e}")
    
    def get_ticker_details(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a ticker"""
        try:
            data = self._make_request(f"/v3/reference/tickers/{symbol}")
            
            if data.get('status') == 'OK' and 'results' in data:
                ticker = data['results']
                return {
                    'symbol': ticker['ticker'],
                    'name': ticker['name'],
                    'description': ticker.get('description', ''),
                    'market': ticker.get('market', ''),
                    'locale': ticker.get('locale', ''),
                    'primary_exchange': ticker.get('primary_exchange', ''),
                    'type': ticker.get('type', ''),
                    'active': ticker.get('active', True),
                    'currency_name': ticker.get('currency_name', 'USD'),
                    'market_cap': ticker.get('market_cap'),
                    'share_class_shares_outstanding': ticker.get('share_class_shares_outstanding'),
                    'weighted_shares_outstanding': ticker.get('weighted_shares_outstanding')
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting ticker details for {symbol}: {e}")
            return None
    
    def get_aggregates(self, symbol: str, timespan: str = 'day', from_date: str = None, to_date: str = None, limit: int = 120) -> Optional[List[Dict[str, Any]]]:
        """Get aggregate bars for a ticker"""
        try:
            if not from_date:
                from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not to_date:
                to_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'timespan': timespan,
                'from': from_date,
                'to': to_date,
                'adjusted': 'true',
                'sort': 'asc',
                'limit': str(limit)
            }
            
            data = self._make_request(f"/v2/aggs/ticker/{symbol}/range/1/{timespan}/{from_date}/{to_date}", params)
            
            if data.get('status') == 'OK' and 'results' in data:
                aggregates = []
                for result in data['results']:
                    aggregates.append({
                        'timestamp': datetime.fromtimestamp(result['t'] / 1000).isoformat(),
                        'open': result['o'],
                        'high': result['h'],
                        'low': result['l'],
                        'close': result['c'],
                        'volume': result['v'],
                        'vwap': result.get('vw', result['c']),  # Volume weighted average price
                        'transactions': result.get('n', 0)
                    })
                return aggregates
            return None
            
        except Exception as e:
            logger.error(f"Error getting aggregates for {symbol}: {e}")
            return None
    
    def get_previous_close(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get previous day's close price"""
        try:
            data = self._make_request(f"/v2/aggs/ticker/{symbol}/prev")
            
            if data.get('status') == 'OK' and 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                return {
                    'symbol': symbol,
                    'close': result['c'],
                    'high': result['h'],
                    'low': result['l'],
                    'open': result['o'],
                    'volume': result['v'],
                    'timestamp': datetime.fromtimestamp(result['t'] / 1000).isoformat()
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting previous close for {symbol}: {e}")
            return None
    
    def search_tickers(self, search: str, market: str = 'stocks', limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Search for tickers"""
        try:
            params = {
                'search': search,
                'market': market,
                'active': 'true',
                'limit': str(limit)
            }
            
            data = self._make_request("/v3/reference/tickers", params)
            
            if data.get('status') == 'OK' and 'results' in data:
                tickers = []
                for ticker in data['results']:
                    tickers.append({
                        'symbol': ticker['ticker'],
                        'name': ticker['name'],
                        'market': ticker.get('market', ''),
                        'locale': ticker.get('locale', ''),
                        'primary_exchange': ticker.get('primary_exchange', ''),
                        'type': ticker.get('type', ''),
                        'active': ticker.get('active', True),
                        'currency_name': ticker.get('currency_name', 'USD')
                    })
                return tickers
            return None
            
        except Exception as e:
            logger.error(f"Error searching tickers for '{search}': {e}")
            return None
    
    def get_market_status(self) -> Optional[Dict[str, Any]]:
        """Get current market status"""
        try:
            data = self._make_request("/v1/marketstatus/now")
            
            if data.get('status') == 'OK' and 'results' in data:
                result = data['results']
                return {
                    'market': result.get('market', ''),
                    'serverTime': result.get('serverTime', ''),
                    'exchanges': result.get('exchanges', {}),
                    'currencies': result.get('currencies', {})
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return None
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API usage status"""
        return {
            'api_key_configured': bool(self.api_key),
            'rate_limit_per_minute': self.rate_limit,
            'last_request_time': datetime.fromtimestamp(self.last_request_time).isoformat() if self.last_request_time else None
        }
