import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.news_api_key = settings.news_api_key
        self.news_api_url = "https://newsapi.org/v2"
        self.use_real_api = bool(self.news_api_key and self.news_api_key != "your_news_api_key_here")
        
    def get_market_news(self, limit: int = 10) -> List[Dict]:
        """Get general market news"""
        try:
            if self.use_real_api:
                return self._get_real_market_news(limit)
            else:
                return self._get_mock_market_news(limit)
        except Exception as e:
            logger.error(f"Error getting market news: {e}")
            return []

    def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get news for a specific stock"""
        try:
            if self.use_real_api:
                return self._get_real_stock_news(symbol, limit)
            else:
                return self._get_mock_stock_news(symbol, limit)
        except Exception as e:
            logger.error(f"Error getting stock news for {symbol}: {e}")
            return []

    def get_crypto_news(self, limit: int = 10) -> List[Dict]:
        """Get cryptocurrency news"""
        try:
            if self.use_real_api:
                return self._get_real_crypto_news(limit)
            else:
                return self._get_mock_crypto_news(limit)
        except Exception as e:
            logger.error(f"Error getting crypto news: {e}")
            return []

    def _get_real_market_news(self, limit: int) -> List[Dict]:
        """Get real market news from NewsAPI"""
        try:
            url = f"{self.news_api_url}/everything"
            params = {
                'q': 'stock market OR finance OR economy OR trading',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': min(limit, 100),  # NewsAPI limit
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return [
                    {
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'sentiment': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', '')),
                        'relevance_score': 0.8  # Default relevance for market news
                    }
                    for article in articles[:limit]
                ]
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return self._get_mock_market_news(limit)
                
        except Exception as e:
            logger.error(f"Error fetching real market news: {e}")
            return self._get_mock_market_news(limit)

    def _get_real_stock_news(self, symbol: str, limit: int) -> List[Dict]:
        """Get real stock news from NewsAPI"""
        try:
            url = f"{self.news_api_url}/everything"
            params = {
                'q': f'"{symbol}" OR "{symbol} stock" OR "{symbol} shares"',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': min(limit, 100),
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return [
                    {
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'sentiment': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', '')),
                        'relevance_score': 0.9  # Higher relevance for stock-specific news
                    }
                    for article in articles[:limit]
                ]
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return self._get_mock_stock_news(symbol, limit)
                
        except Exception as e:
            logger.error(f"Error fetching real stock news for {symbol}: {e}")
            return self._get_mock_stock_news(symbol, limit)

    def _get_real_crypto_news(self, limit: int) -> List[Dict]:
        """Get real crypto news from NewsAPI"""
        try:
            url = f"{self.news_api_url}/everything"
            params = {
                'q': 'cryptocurrency OR bitcoin OR ethereum OR crypto OR blockchain',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': min(limit, 100),
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return [
                    {
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'sentiment': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', '')),
                        'relevance_score': 0.8
                    }
                    for article in articles[:limit]
                ]
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return self._get_mock_crypto_news(limit)
                
        except Exception as e:
            logger.error(f"Error fetching real crypto news: {e}")
            return self._get_mock_crypto_news(limit)

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis for news text"""
        if not text:
            return "neutral"
        
        positive_words = ['strong', 'growth', 'surge', 'rise', 'gain', 'positive', 'bullish', 'upgrade', 'beat', 'exceed', 'profit', 'success', 'breakthrough', 'innovation', 'expansion']
        negative_words = ['fall', 'drop', 'decline', 'loss', 'negative', 'bearish', 'downgrade', 'miss', 'concern', 'risk', 'crisis', 'failure', 'recession', 'crash', 'volatility']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _get_mock_market_news(self, limit: int) -> List[Dict]:
        """Generate mock market news for development"""
        mock_news = [
            {
                "title": "Federal Reserve Signals Potential Rate Cut Amid Economic Uncertainty",
                "summary": "The Federal Reserve hinted at possible interest rate adjustments in response to recent economic indicators showing mixed signals about inflation and growth.",
                "source": "Financial Times",
                "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "url": "https://example.com/news/1",
                "sentiment": "neutral",
                "relevance_score": 0.95
            },
            {
                "title": "Tech Stocks Rally as AI Investments Surge",
                "summary": "Major technology companies see significant gains as artificial intelligence investments continue to drive market optimism and investor confidence.",
                "source": "Wall Street Journal",
                "published_at": (datetime.now() - timedelta(hours=4)).isoformat(),
                "url": "https://example.com/news/2",
                "sentiment": "positive",
                "relevance_score": 0.88
            },
            {
                "title": "Energy Sector Faces Volatility Amid Geopolitical Tensions",
                "summary": "Oil and gas companies experience price fluctuations as global energy markets respond to ongoing geopolitical developments and supply chain concerns.",
                "source": "Reuters",
                "published_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                "url": "https://example.com/news/3",
                "sentiment": "negative",
                "relevance_score": 0.82
            },
            {
                "title": "Healthcare Stocks Show Resilience in Q3 Earnings",
                "summary": "Healthcare sector demonstrates strong performance with several companies reporting better-than-expected quarterly results and optimistic outlooks.",
                "source": "Bloomberg",
                "published_at": (datetime.now() - timedelta(hours=8)).isoformat(),
                "url": "https://example.com/news/4",
                "sentiment": "positive",
                "relevance_score": 0.79
            },
            {
                "title": "Banking Sector Prepares for New Regulatory Framework",
                "summary": "Major banks are adapting to upcoming regulatory changes that could impact lending practices and capital requirements across the financial industry.",
                "source": "CNBC",
                "published_at": (datetime.now() - timedelta(hours=10)).isoformat(),
                "url": "https://example.com/news/5",
                "sentiment": "neutral",
                "relevance_score": 0.85
            }
        ]
        
        return mock_news[:limit]

    def _get_mock_stock_news(self, symbol: str, limit: int) -> List[Dict]:
        """Generate mock stock-specific news"""
        company_names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "TSLA": "Tesla Inc.",
            "META": "Meta Platforms Inc.",
            "NVDA": "NVIDIA Corporation",
            "NFLX": "Netflix Inc."
        }
        
        company_name = company_names.get(symbol, f"{symbol} Corporation")
        
        mock_news = [
            {
                "title": f"{company_name} Reports Strong Q3 Performance",
                "summary": f"{company_name} announced better-than-expected quarterly results, with revenue growth exceeding analyst projections and strong guidance for the upcoming quarter.",
                "source": "MarketWatch",
                "published_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "url": f"https://example.com/news/{symbol.lower()}/1",
                "sentiment": "positive",
                "relevance_score": 0.92
            },
            {
                "title": f"Analysts Upgrade {company_name} Price Target",
                "summary": f"Several Wall Street analysts have raised their price targets for {company_name} following recent developments and positive industry trends.",
                "source": "Seeking Alpha",
                "published_at": (datetime.now() - timedelta(hours=3)).isoformat(),
                "url": f"https://example.com/news/{symbol.lower()}/2",
                "sentiment": "positive",
                "relevance_score": 0.87
            },
            {
                "title": f"{company_name} Announces New Strategic Partnership",
                "summary": f"{company_name} revealed a new partnership agreement that could significantly impact the company's market position and future growth prospects.",
                "source": "Business Wire",
                "published_at": (datetime.now() - timedelta(hours=5)).isoformat(),
                "url": f"https://example.com/news/{symbol.lower()}/3",
                "sentiment": "positive",
                "relevance_score": 0.84
            },
            {
                "title": f"Market Volatility Affects {company_name} Trading",
                "summary": f"{company_name} shares experienced increased volatility as broader market conditions and sector-specific factors influenced trading activity.",
                "source": "Yahoo Finance",
                "published_at": (datetime.now() - timedelta(hours=7)).isoformat(),
                "url": f"https://example.com/news/{symbol.lower()}/4",
                "sentiment": "neutral",
                "relevance_score": 0.76
            },
            {
                "title": f"{company_name} CEO Discusses Future Growth Strategy",
                "summary": f"The CEO of {company_name} outlined the company's strategic vision and growth initiatives during a recent investor conference, highlighting key priorities for the coming year.",
                "source": "Investor Relations",
                "published_at": (datetime.now() - timedelta(hours=9)).isoformat(),
                "url": f"https://example.com/news/{symbol.lower()}/5",
                "sentiment": "positive",
                "relevance_score": 0.89
            }
        ]
        
        return mock_news[:limit]

    def _get_mock_crypto_news(self, limit: int) -> List[Dict]:
        """Generate mock cryptocurrency news"""
        mock_news = [
            {
                "title": "Bitcoin Surges Past Key Resistance Level",
                "summary": "Bitcoin breaks through significant resistance as institutional adoption continues to grow and regulatory clarity improves in major markets.",
                "source": "CoinDesk",
                "published_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "url": "https://example.com/crypto/1",
                "sentiment": "positive",
                "relevance_score": 0.94
            },
            {
                "title": "Ethereum Network Upgrade Shows Promising Results",
                "summary": "The latest Ethereum network upgrade demonstrates improved transaction speeds and reduced gas fees, boosting developer confidence in the platform.",
                "source": "Decrypt",
                "published_at": (datetime.now() - timedelta(hours=3)).isoformat(),
                "url": "https://example.com/crypto/2",
                "sentiment": "positive",
                "relevance_score": 0.91
            },
            {
                "title": "Regulatory Developments Shape Crypto Market Outlook",
                "summary": "New regulatory frameworks in key jurisdictions are providing clearer guidelines for cryptocurrency adoption and institutional investment.",
                "source": "CryptoSlate",
                "published_at": (datetime.now() - timedelta(hours=5)).isoformat(),
                "url": "https://example.com/crypto/3",
                "sentiment": "neutral",
                "relevance_score": 0.86
            },
            {
                "title": "DeFi Protocols See Increased TVL and User Activity",
                "summary": "Decentralized finance protocols report growing total value locked and user engagement as the sector continues to mature and expand.",
                "source": "DeFi Pulse",
                "published_at": (datetime.now() - timedelta(hours=7)).isoformat(),
                "url": "https://example.com/crypto/4",
                "sentiment": "positive",
                "relevance_score": 0.83
            },
            {
                "title": "NFT Market Shows Signs of Recovery",
                "summary": "The non-fungible token market demonstrates renewed interest as new use cases and improved infrastructure attract both creators and collectors.",
                "source": "NFT Now",
                "published_at": (datetime.now() - timedelta(hours=9)).isoformat(),
                "url": "https://example.com/crypto/5",
                "sentiment": "positive",
                "relevance_score": 0.78
            }
        ]
        
        return mock_news[:limit]

    def get_news_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of news text (mock implementation)"""
        # In production, you would use a real sentiment analysis API
        positive_words = ['strong', 'growth', 'surge', 'rise', 'gain', 'positive', 'bullish', 'upgrade', 'beat', 'exceed']
        negative_words = ['fall', 'drop', 'decline', 'loss', 'negative', 'bearish', 'downgrade', 'miss', 'concern', 'risk']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": min(0.95, 0.6 + abs(positive_count - negative_count) * 0.05)
        }

    def search_news(self, query: str, limit: int = 10, sort_by: str = "publishedAt") -> List[Dict]:
        """Search for news articles"""
        try:
            if self.use_real_api:
                return self._search_real_news(query, limit, sort_by)
            else:
                return self._search_mock_news(query, limit)
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []

    def filter_news(self, category: str = None, source: str = None, sentiment: str = None, limit: int = 10) -> List[Dict]:
        """Filter news by category, source, or sentiment"""
        try:
            if self.use_real_api:
                return self._filter_real_news(category, source, sentiment, limit)
            else:
                return self._filter_mock_news(category, source, sentiment, limit)
        except Exception as e:
            logger.error(f"Error filtering news: {e}")
            return []

    def _search_real_news(self, query: str, limit: int, sort_by: str) -> List[Dict]:
        """Search real news from NewsAPI"""
        try:
            url = f"{self.news_api_url}/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': sort_by,
                'pageSize': min(limit, 100),
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return [
                    {
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'sentiment': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', '')),
                        'relevance_score': 0.8
                    }
                    for article in articles[:limit]
                ]
            else:
                logger.error(f"NewsAPI search error: {data.get('message', 'Unknown error')}")
                return self._search_mock_news(query, limit)
                
        except Exception as e:
            logger.error(f"Error searching real news: {e}")
            return self._search_mock_news(query, limit)

    def _filter_real_news(self, category: str, source: str, sentiment: str, limit: int) -> List[Dict]:
        """Filter real news from NewsAPI"""
        try:
            # Build query based on filters
            query_parts = []
            if category:
                query_parts.append(category)
            if source:
                query_parts.append(f'source:"{source}"')
            
            query = ' AND '.join(query_parts) if query_parts else 'news'
            
            url = f"{self.news_api_url}/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': min(limit, 100),
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                filtered_articles = []
                
                for article in articles:
                    article_sentiment = self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', ''))
                    
                    # Apply sentiment filter
                    if sentiment and article_sentiment != sentiment:
                        continue
                    
                    filtered_articles.append({
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'sentiment': article_sentiment,
                        'relevance_score': 0.8
                    })
                
                return filtered_articles[:limit]
            else:
                logger.error(f"NewsAPI filter error: {data.get('message', 'Unknown error')}")
                return self._filter_mock_news(category, source, sentiment, limit)
                
        except Exception as e:
            logger.error(f"Error filtering real news: {e}")
            return self._filter_mock_news(category, source, sentiment, limit)

    def _search_mock_news(self, query: str, limit: int) -> List[Dict]:
        """Search mock news for development"""
        # Simple mock search - filter existing mock news by query
        all_mock_news = self._get_mock_market_news(50)
        filtered_news = [
            article for article in all_mock_news
            if query.lower() in article['title'].lower() or query.lower() in article['summary'].lower()
        ]
        return filtered_news[:limit]

    def _filter_mock_news(self, category: str, source: str, sentiment: str, limit: int) -> List[Dict]:
        """Filter mock news for development"""
        all_mock_news = self._get_mock_market_news(50)
        filtered_news = all_mock_news
        
        if sentiment:
            filtered_news = [article for article in filtered_news if article.get('sentiment') == sentiment]
        
        if source:
            filtered_news = [article for article in filtered_news if source.lower() in article.get('source', '').lower()]
        
        return filtered_news[:limit]
