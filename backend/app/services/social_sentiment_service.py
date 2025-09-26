import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
from app.core.config import settings

logger = logging.getLogger(__name__)

class SocialSentimentService:
    def __init__(self):
        self.reddit_client_id = getattr(settings, 'reddit_client_id', None)
        self.reddit_client_secret = getattr(settings, 'reddit_client_secret', None)
        self.twitter_bearer_token = getattr(settings, 'twitter_bearer_token', None)
        self.openai_api_key = settings.openai_api_key

    def get_reddit_sentiment(self, symbol: str, limit: int = 100) -> Dict:
        """Get Reddit sentiment for a symbol"""
        try:
            if not self.reddit_client_id or not self.reddit_client_secret:
                return self._get_mock_reddit_sentiment(symbol, limit)

            # Get Reddit access token
            auth_url = "https://www.reddit.com/api/v1/access_token"
            auth_data = {
                'grant_type': 'client_credentials'
            }
            auth_headers = {
                'User-Agent': 'StockeeApp/1.0'
            }
            
            response = requests.post(
                auth_url,
                data=auth_data,
                headers=auth_headers,
                auth=(self.reddit_client_id, self.reddit_client_secret),
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Reddit auth failed: {response.status_code}")
                return self._get_mock_reddit_sentiment(symbol, limit)
            
            access_token = response.json()['access_token']
            
            # Search Reddit for posts about the symbol
            search_url = f"https://oauth.reddit.com/search"
            search_headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'StockeeApp/1.0'
            }
            search_params = {
                'q': symbol,
                'sort': 'new',
                'limit': limit,
                't': 'week'  # Last week
            }
            
            response = requests.get(
                search_url,
                headers=search_headers,
                params=search_params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Reddit search failed: {response.status_code}")
                return self._get_mock_reddit_sentiment(symbol, limit)
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            # Analyze sentiment
            sentiment_data = self._analyze_reddit_sentiment(posts, symbol)
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error getting Reddit sentiment for {symbol}: {e}")
            return self._get_mock_reddit_sentiment(symbol, limit)

    def get_twitter_sentiment(self, symbol: str, limit: int = 100) -> Dict:
        """Get Twitter sentiment for a symbol"""
        try:
            if not self.twitter_bearer_token:
                return self._get_mock_twitter_sentiment(symbol, limit)

            # Search Twitter for tweets about the symbol
            search_url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}'
            }
            params = {
                'query': f'${symbol} OR {symbol}',
                'max_results': min(limit, 100),
                'tweet.fields': 'created_at,public_metrics,context_annotations'
            }
            
            response = requests.get(
                search_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Twitter search failed: {response.status_code}")
                return self._get_mock_twitter_sentiment(symbol, limit)
            
            data = response.json()
            tweets = data.get('data', [])
            
            # Analyze sentiment
            sentiment_data = self._analyze_twitter_sentiment(tweets, symbol)
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error getting Twitter sentiment for {symbol}: {e}")
            return self._get_mock_twitter_sentiment(symbol, limit)

    def _analyze_reddit_sentiment(self, posts: List[Dict], symbol: str) -> Dict:
        """Analyze Reddit posts for sentiment"""
        try:
            if not posts:
                return self._get_mock_reddit_sentiment(symbol, 0)

            total_posts = len(posts)
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            post_data = []
            
            for post in posts[:50]:  # Limit to 50 posts for analysis
                post_info = post.get('data', {})
                title = post_info.get('title', '')
                selftext = post_info.get('selftext', '')
                score = post_info.get('score', 0)
                num_comments = post_info.get('num_comments', 0)
                created_utc = post_info.get('created_utc', 0)
                
                # Combine title and text for analysis
                text = f"{title} {selftext}".strip()
                
                if text:
                    # Simple sentiment analysis using keywords
                    sentiment = self._analyze_text_sentiment(text)
                    
                    if sentiment == 'positive':
                        positive_count += 1
                    elif sentiment == 'negative':
                        negative_count += 1
                    else:
                        neutral_count += 1
                    
                    post_data.append({
                        'title': title[:100] + '...' if len(title) > 100 else title,
                        'score': score,
                        'num_comments': num_comments,
                        'sentiment': sentiment,
                        'created_at': datetime.fromtimestamp(created_utc).isoformat(),
                        'subreddit': post_info.get('subreddit', 'unknown')
                    })
            
            # Calculate overall sentiment
            if total_posts > 0:
                positive_ratio = positive_count / total_posts
                negative_ratio = negative_count / total_posts
                neutral_ratio = neutral_count / total_posts
                
                if positive_ratio > negative_ratio:
                    overall_sentiment = 'bullish'
                    sentiment_score = positive_ratio
                elif negative_ratio > positive_ratio:
                    overall_sentiment = 'bearish'
                    sentiment_score = negative_ratio
                else:
                    overall_sentiment = 'neutral'
                    sentiment_score = neutral_ratio
            else:
                overall_sentiment = 'neutral'
                sentiment_score = 0.5
            
            return {
                'symbol': symbol,
                'platform': 'reddit',
                'total_posts': total_posts,
                'positive_posts': positive_count,
                'negative_posts': negative_count,
                'neutral_posts': neutral_count,
                'overall_sentiment': overall_sentiment,
                'sentiment_score': round(sentiment_score, 3),
                'posts': post_data[:10],  # Return top 10 posts
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Reddit sentiment: {e}")
            return self._get_mock_reddit_sentiment(symbol, 0)

    def _analyze_twitter_sentiment(self, tweets: List[Dict], symbol: str) -> Dict:
        """Analyze Twitter tweets for sentiment"""
        try:
            if not tweets:
                return self._get_mock_twitter_sentiment(symbol, 0)

            total_tweets = len(tweets)
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            tweet_data = []
            
            for tweet in tweets:
                text = tweet.get('text', '')
                created_at = tweet.get('created_at', '')
                public_metrics = tweet.get('public_metrics', {})
                
                if text:
                    # Simple sentiment analysis using keywords
                    sentiment = self._analyze_text_sentiment(text)
                    
                    if sentiment == 'positive':
                        positive_count += 1
                    elif sentiment == 'negative':
                        negative_count += 1
                    else:
                        neutral_count += 1
                    
                    tweet_data.append({
                        'text': text[:100] + '...' if len(text) > 100 else text,
                        'retweet_count': public_metrics.get('retweet_count', 0),
                        'like_count': public_metrics.get('like_count', 0),
                        'reply_count': public_metrics.get('reply_count', 0),
                        'sentiment': sentiment,
                        'created_at': created_at
                    })
            
            # Calculate overall sentiment
            if total_tweets > 0:
                positive_ratio = positive_count / total_tweets
                negative_ratio = negative_count / total_tweets
                neutral_ratio = neutral_count / total_tweets
                
                if positive_ratio > negative_ratio:
                    overall_sentiment = 'bullish'
                    sentiment_score = positive_ratio
                elif negative_ratio > positive_ratio:
                    overall_sentiment = 'bearish'
                    sentiment_score = negative_ratio
                else:
                    overall_sentiment = 'neutral'
                    sentiment_score = neutral_ratio
            else:
                overall_sentiment = 'neutral'
                sentiment_score = 0.5
            
            return {
                'symbol': symbol,
                'platform': 'twitter',
                'total_tweets': total_tweets,
                'positive_tweets': positive_count,
                'negative_tweets': negative_count,
                'neutral_tweets': neutral_count,
                'overall_sentiment': overall_sentiment,
                'sentiment_score': round(sentiment_score, 3),
                'tweets': tweet_data[:10],  # Return top 10 tweets
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Twitter sentiment: {e}")
            return self._get_mock_twitter_sentiment(symbol, 0)

    def _analyze_text_sentiment(self, text: str) -> str:
        """Analyze text sentiment using keyword matching"""
        try:
            # Convert to lowercase for analysis
            text_lower = text.lower()
            
            # Positive keywords
            positive_keywords = [
                'bullish', 'buy', 'long', 'moon', 'rocket', 'pump', 'gains', 'profit',
                'up', 'rise', 'surge', 'rally', 'breakout', 'breakthrough', 'strong',
                'good', 'great', 'excellent', 'amazing', 'love', 'best', 'winner',
                'growth', 'earnings', 'beat', 'exceed', 'outperform', 'upgrade'
            ]
            
            # Negative keywords
            negative_keywords = [
                'bearish', 'sell', 'short', 'crash', 'dump', 'loss', 'down', 'fall',
                'drop', 'decline', 'weak', 'bad', 'terrible', 'awful', 'hate', 'worst',
                'loser', 'miss', 'disappoint', 'downgrade', 'cut', 'reduce', 'bear'
            ]
            
            # Count positive and negative keywords
            positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
            
            # Determine sentiment
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return 'neutral'

    def get_combined_sentiment(self, symbol: str) -> Dict:
        """Get combined sentiment from Reddit and Twitter"""
        try:
            reddit_sentiment = self.get_reddit_sentiment(symbol, 50)
            twitter_sentiment = self.get_twitter_sentiment(symbol, 50)
            
            # Combine sentiment scores
            reddit_score = reddit_sentiment.get('sentiment_score', 0.5)
            twitter_score = twitter_sentiment.get('sentiment_score', 0.5)
            
            # Weighted average (Reddit 60%, Twitter 40%)
            combined_score = (reddit_score * 0.6) + (twitter_score * 0.4)
            
            # Determine overall sentiment
            if combined_score > 0.6:
                overall_sentiment = 'bullish'
            elif combined_score < 0.4:
                overall_sentiment = 'bearish'
            else:
                overall_sentiment = 'neutral'
            
            return {
                'symbol': symbol,
                'overall_sentiment': overall_sentiment,
                'combined_score': round(combined_score, 3),
                'reddit_sentiment': reddit_sentiment,
                'twitter_sentiment': twitter_sentiment,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting combined sentiment for {symbol}: {e}")
            return {
                'symbol': symbol,
                'overall_sentiment': 'neutral',
                'combined_score': 0.5,
                'error': str(e)
            }

    def _get_mock_reddit_sentiment(self, symbol: str, limit: int) -> Dict:
        """Get mock Reddit sentiment data"""
        import random
        
        positive_count = random.randint(10, 30)
        negative_count = random.randint(5, 20)
        neutral_count = limit - positive_count - negative_count
        
        overall_sentiment = 'bullish' if positive_count > negative_count else 'bearish' if negative_count > positive_count else 'neutral'
        sentiment_score = positive_count / limit if overall_sentiment == 'bullish' else negative_count / limit if overall_sentiment == 'bearish' else 0.5
        
        return {
            'symbol': symbol,
            'platform': 'reddit',
            'total_posts': limit,
            'positive_posts': positive_count,
            'negative_posts': negative_count,
            'neutral_posts': neutral_count,
            'overall_sentiment': overall_sentiment,
            'sentiment_score': round(sentiment_score, 3),
            'posts': [],
            'timestamp': datetime.now().isoformat(),
            'note': 'Mock data - Reddit API not configured'
        }

    def _get_mock_twitter_sentiment(self, symbol: str, limit: int) -> Dict:
        """Get mock Twitter sentiment data"""
        import random
        
        positive_count = random.randint(15, 35)
        negative_count = random.randint(8, 25)
        neutral_count = limit - positive_count - negative_count
        
        overall_sentiment = 'bullish' if positive_count > negative_count else 'bearish' if negative_count > positive_count else 'neutral'
        sentiment_score = positive_count / limit if overall_sentiment == 'bullish' else negative_count / limit if overall_sentiment == 'bearish' else 0.5
        
        return {
            'symbol': symbol,
            'platform': 'twitter',
            'total_tweets': limit,
            'positive_tweets': positive_count,
            'negative_tweets': negative_count,
            'neutral_tweets': neutral_count,
            'overall_sentiment': overall_sentiment,
            'sentiment_score': round(sentiment_score, 3),
            'tweets': [],
            'timestamp': datetime.now().isoformat(),
            'note': 'Mock data - Twitter API not configured'
        }
