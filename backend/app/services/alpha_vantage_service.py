import requests
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

class AlphaVantageService:
    """Enhanced Alpha Vantage API service with rate limiting and caching"""
    
    def __init__(self):
        self.api_key = settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit = int(os.getenv("ALPHA_VANTAGE_RATE_LIMIT", "5"))
        self.daily_limit = int(os.getenv("ALPHA_VANTAGE_DAILY_LIMIT", "500"))
        self.last_request_time = 0
        self.request_count = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
    def _rate_limit_check(self):
        """Implement rate limiting"""
        now = time.time()
        
        # Reset daily counter if new day
        if datetime.now() >= self.daily_reset_time + timedelta(days=1):
            self.request_count = 0
            self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check daily limit
        if self.request_count >= self.daily_limit:
            raise Exception(f"Daily API limit reached ({self.daily_limit} requests)")
        
        # Check rate limit (requests per minute)
        if now - self.last_request_time < 60 / self.rate_limit:
            sleep_time = (60 / self.rate_limit) - (now - self.last_request_time)
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make API request with rate limiting"""
        self._rate_limit_check()
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                raise Exception(f"Alpha Vantage API Error: {data['Error Message']}")
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage API Note: {data['Note']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage API request failed: {e}")
            raise Exception(f"Failed to fetch data from Alpha Vantage: {e}")
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price and quote data"""
        try:
            data = self._make_request({
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol
            })
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': symbol,
                    'price': float(quote['05. price']),
                    'change': float(quote['09. change']),
                    'change_percent': float(quote['10. change percent'].replace('%', '')),
                    'volume': int(quote['06. volume']),
                    'high': float(quote['03. high']),
                    'low': float(quote['04. low']),
                    'open': float(quote['02. open']),
                    'previous_close': float(quote['08. previous close']),
                    'timestamp': datetime.now().isoformat()
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def get_daily_data(self, symbol: str, outputsize: str = 'compact') -> Optional[List[Dict[str, Any]]]:
        """Get daily OHLCV data"""
        try:
            data = self._make_request({
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': outputsize  # 'compact' (100 days) or 'full' (20+ years)
            })
            
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                daily_data = []
                
                for date_str, values in time_series.items():
                    daily_data.append({
                        'date': date_str,
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume'])
                    })
                
                # Sort by date (oldest first)
                daily_data.sort(key=lambda x: x['date'])
                return daily_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting daily data for {symbol}: {e}")
            return None
    
    def get_intraday_data(self, symbol: str, interval: str = '5min', outputsize: str = 'compact') -> Optional[List[Dict[str, Any]]]:
        """Get intraday OHLCV data"""
        try:
            data = self._make_request({
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize
            })
            
            if f'Time Series ({interval})' in data:
                time_series = data[f'Time Series ({interval})']
                intraday_data = []
                
                for timestamp_str, values in time_series.items():
                    intraday_data.append({
                        'timestamp': timestamp_str,
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume'])
                    })
                
                # Sort by timestamp (oldest first)
                intraday_data.sort(key=lambda x: x['timestamp'])
                return intraday_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting intraday data for {symbol}: {e}")
            return None
    
    def search_symbols(self, keywords: str) -> Optional[List[Dict[str, Any]]]:
        """Search for stock symbols"""
        try:
            data = self._make_request({
                'function': 'SYMBOL_SEARCH',
                'keywords': keywords
            })
            
            if 'bestMatches' in data:
                matches = []
                for match in data['bestMatches']:
                    matches.append({
                        'symbol': match['1. symbol'],
                        'name': match['2. name'],
                        'type': match['3. type'],
                        'region': match['4. region'],
                        'market_open': match['5. marketOpen'],
                        'market_close': match['6. marketClose'],
                        'timezone': match['7. timezone'],
                        'currency': match['8. currency'],
                        'match_score': float(match['9. matchScore'])
                    })
                return matches
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching symbols for '{keywords}': {e}")
            return None
    
    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company overview and key metrics"""
        try:
            data = self._make_request({
                'function': 'OVERVIEW',
                'symbol': symbol
            })
            
            if data and 'Symbol' in data:
                return {
                    'symbol': data['Symbol'],
                    'name': data['Name'],
                    'description': data['Description'],
                    'sector': data['Sector'],
                    'industry': data['Industry'],
                    'market_cap': data['MarketCapitalization'],
                    'pe_ratio': data['PERatio'],
                    'dividend_yield': data['DividendYield'],
                    'beta': data['Beta'],
                    '52_week_high': data['52WeekHigh'],
                    '52_week_low': data['52WeekLow'],
                    'analyst_target_price': data['AnalystTargetPrice'],
                    'eps': data['EPS'],
                    'revenue_ttm': data['RevenueTTM'],
                    'profit_margin': data['ProfitMargin']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting company overview for {symbol}: {e}")
            return None
    
    def get_technical_indicators(self, symbol: str, function: str, interval: str = 'daily', time_period: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Get technical indicators (SMA, EMA, RSI, MACD, etc.)"""
        try:
            params = {
                'function': function,
                'symbol': symbol,
                'interval': interval,
                'time_period': str(time_period)
            }
            
            # Add series_type for some indicators
            if function in ['SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'MAMA', 'T3']:
                params['series_type'] = 'close'
            
            data = self._make_request(params)
            
            # Extract the appropriate time series based on function
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key or 'Technical Analysis' in key:
                    time_series_key = key
                    break
            
            if time_series_key and data[time_series_key]:
                indicators = []
                for date_str, values in data[time_series_key].items():
                    indicator_data = {'date': date_str}
                    for key, value in values.items():
                        try:
                            indicator_data[key] = float(value)
                        except (ValueError, TypeError):
                            indicator_data[key] = value
                    indicators.append(indicator_data)
                
                # Sort by date (oldest first)
                indicators.sort(key=lambda x: x['date'])
                return indicators
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting {function} for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, days: int = 30) -> Optional[List[Dict]]:
        """Get historical daily data for a symbol"""
        try:
            self._rate_limit_check()
            
            url = f"{self.base_url}/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key,
                'outputsize': 'compact' if days <= 30 else 'full'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                logger.error(f"No time series data found for {symbol}")
                return None
            
            # Convert to list format
            historical_data = []
            for date, values in list(time_series.items())[:days]:
                historical_data.append({
                    'date': date,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            # Sort by date (oldest first)
            historical_data.sort(key=lambda x: x['date'])
            
            logger.info(f"Retrieved {len(historical_data)} days of historical data for {symbol}")
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None

    def get_api_status(self) -> Dict[str, Any]:
        """Get API usage status"""
        return {
            'requests_today': self.request_count,
            'daily_limit': self.daily_limit,
            'rate_limit_per_minute': self.rate_limit,
            'last_request_time': datetime.fromtimestamp(self.last_request_time).isoformat() if self.last_request_time else None,
            'daily_reset_time': self.daily_reset_time.isoformat()
        }
