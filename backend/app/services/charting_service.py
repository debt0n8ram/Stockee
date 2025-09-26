import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ChartingService:
    def __init__(self, db: Session):
        self.db = db

    def get_candlestick_data(self, symbol: str, timeframe: str = '1d', days: int = 30) -> Dict:
        """Get candlestick data for advanced charting"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return {"error": "Asset not found"}

            # Calculate start date based on timeframe
            end_date = datetime.utcnow()
            if timeframe == '1m':
                start_date = end_date - timedelta(minutes=days)
            elif timeframe == '5m':
                start_date = end_date - timedelta(minutes=days * 5)
            elif timeframe == '15m':
                start_date = end_date - timedelta(minutes=days * 15)
            elif timeframe == '1h':
                start_date = end_date - timedelta(hours=days)
            elif timeframe == '4h':
                start_date = end_date - timedelta(hours=days * 4)
            elif timeframe == '1d':
                start_date = end_date - timedelta(days=days)
            elif timeframe == '1w':
                start_date = end_date - timedelta(weeks=days)
            else:
                start_date = end_date - timedelta(days=days)

            # Get price data
            prices = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            ).order_by(models.Price.timestamp).all()

            if not prices:
                return {"error": "No price data available"}

            # Convert to DataFrame for processing
            df = pd.DataFrame([
                {
                    'timestamp': price.timestamp,
                    'open': float(price.open_price),
                    'high': float(price.high_price),
                    'low': float(price.low_price),
                    'close': float(price.close_price),
                    'volume': int(price.volume) if price.volume else 0
                }
                for price in prices
            ])

            # Resample data based on timeframe
            df.set_index('timestamp', inplace=True)
            
            if timeframe in ['1m', '5m', '15m', '1h', '4h']:
                # For intraday timeframes, resample to the specified interval
                freq_map = {
                    '1m': '1T',
                    '5m': '5T',
                    '15m': '15T',
                    '1h': '1H',
                    '4h': '4H'
                }
                freq = freq_map.get(timeframe, '1H')
                
                # Resample OHLCV data
                resampled = df.resample(freq).agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
            else:
                resampled = df

            # Convert to candlestick format
            candlesticks = []
            for timestamp, row in resampled.iterrows():
                candlesticks.append({
                    'timestamp': timestamp.isoformat(),
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume']
                })

            # Calculate technical indicators for the chart
            indicators = self._calculate_chart_indicators(resampled)

            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'candlesticks': candlesticks,
                'indicators': indicators,
                'data_points': len(candlesticks)
            }

        except Exception as e:
            logger.error(f"Error getting candlestick data for {symbol}: {e}")
            return {"error": f"Failed to get chart data: {str(e)}"}

    def _calculate_chart_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators for chart overlay"""
        try:
            indicators = {}
            
            if len(df) < 20:
                return indicators

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']

            # Moving Averages
            indicators['sma_20'] = close.rolling(window=20).mean().fillna(0).tolist()
            indicators['sma_50'] = close.rolling(window=50).mean().fillna(0).tolist()
            indicators['ema_12'] = close.ewm(span=12).mean().fillna(0).tolist()
            indicators['ema_26'] = close.ewm(span=26).mean().fillna(0).tolist()

            # Bollinger Bands
            sma_20 = close.rolling(window=20).mean()
            std_20 = close.rolling(window=20).std()
            indicators['bb_upper'] = (sma_20 + (std_20 * 2)).fillna(0).tolist()
            indicators['bb_middle'] = sma_20.fillna(0).tolist()
            indicators['bb_lower'] = (sma_20 - (std_20 * 2)).fillna(0).tolist()

            # MACD
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line

            indicators['macd'] = macd_line.fillna(0).tolist()
            indicators['macd_signal'] = signal_line.fillna(0).tolist()
            indicators['macd_histogram'] = histogram.fillna(0).tolist()

            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = rsi.fillna(50).tolist()

            # Volume indicators
            indicators['volume_sma'] = volume.rolling(window=20).mean().fillna(0).tolist()

            return indicators

        except Exception as e:
            logger.error(f"Error calculating chart indicators: {e}")
            return {}

    def get_chart_patterns(self, symbol: str, days: int = 30) -> Dict:
        """Detect chart patterns"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return {"error": "Asset not found"}

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            prices = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            ).order_by(models.Price.timestamp).all()

            if len(prices) < 20:
                return {"patterns": [], "error": "Insufficient data"}

            df = pd.DataFrame([
                {
                    'timestamp': price.timestamp,
                    'open': float(price.open_price),
                    'high': float(price.high_price),
                    'low': float(price.low_price),
                    'close': float(price.close_price),
                    'volume': int(price.volume) if price.volume else 0
                }
                for price in prices
            ])

            patterns = []

            # Head and Shoulders
            if self._detect_head_shoulders(df):
                patterns.append({
                    'name': 'Head and Shoulders',
                    'type': 'reversal',
                    'signal': 'bearish',
                    'confidence': 0.7
                })

            # Double Top/Bottom
            if self._detect_double_top(df):
                patterns.append({
                    'name': 'Double Top',
                    'type': 'reversal',
                    'signal': 'bearish',
                    'confidence': 0.6
                })

            if self._detect_double_bottom(df):
                patterns.append({
                    'name': 'Double Bottom',
                    'type': 'reversal',
                    'signal': 'bullish',
                    'confidence': 0.6
                })

            # Triangle patterns
            triangle = self._detect_triangle(df)
            if triangle:
                patterns.append(triangle)

            # Support and Resistance levels
            support_resistance = self._find_support_resistance(df)
            patterns.extend(support_resistance)

            return {
                'symbol': symbol,
                'patterns': patterns,
                'pattern_count': len(patterns)
            }

        except Exception as e:
            logger.error(f"Error detecting chart patterns for {symbol}: {e}")
            return {"error": f"Failed to detect patterns: {str(e)}"}

    def _detect_head_shoulders(self, df: pd.DataFrame) -> bool:
        """Detect Head and Shoulders pattern"""
        try:
            if len(df) < 20:
                return False

            highs = df['high'].rolling(window=5).max()
            peaks = []

            # Find peaks
            for i in range(2, len(highs) - 2):
                if (highs.iloc[i] > highs.iloc[i-1] and 
                    highs.iloc[i] > highs.iloc[i-2] and
                    highs.iloc[i] > highs.iloc[i+1] and 
                    highs.iloc[i] > highs.iloc[i+2]):
                    peaks.append((i, highs.iloc[i]))

            if len(peaks) < 3:
                return False

            # Check for Head and Shoulders pattern
            # Left shoulder, head, right shoulder
            for i in range(len(peaks) - 2):
                left_shoulder = peaks[i]
                head = peaks[i + 1]
                right_shoulder = peaks[i + 2]

                # Head should be higher than shoulders
                if (head[1] > left_shoulder[1] and 
                    head[1] > right_shoulder[1] and
                    abs(left_shoulder[1] - right_shoulder[1]) / left_shoulder[1] < 0.05):  # Shoulders similar height
                    return True

            return False

        except Exception as e:
            logger.error(f"Error detecting head and shoulders: {e}")
            return False

    def _detect_double_top(self, df: pd.DataFrame) -> bool:
        """Detect Double Top pattern"""
        try:
            if len(df) < 20:
                return False

            highs = df['high'].rolling(window=5).max()
            peaks = []

            # Find peaks
            for i in range(2, len(highs) - 2):
                if (highs.iloc[i] > highs.iloc[i-1] and 
                    highs.iloc[i] > highs.iloc[i-2] and
                    highs.iloc[i] > highs.iloc[i+1] and 
                    highs.iloc[i] > highs.iloc[i+2]):
                    peaks.append((i, highs.iloc[i]))

            if len(peaks) < 2:
                return False

            # Check for double top
            for i in range(len(peaks) - 1):
                peak1 = peaks[i]
                peak2 = peaks[i + 1]

                # Peaks should be similar height
                if abs(peak1[1] - peak2[1]) / peak1[1] < 0.03:
                    return True

            return False

        except Exception as e:
            logger.error(f"Error detecting double top: {e}")
            return False

    def _detect_double_bottom(self, df: pd.DataFrame) -> bool:
        """Detect Double Bottom pattern"""
        try:
            if len(df) < 20:
                return False

            lows = df['low'].rolling(window=5).min()
            troughs = []

            # Find troughs
            for i in range(2, len(lows) - 2):
                if (lows.iloc[i] < lows.iloc[i-1] and 
                    lows.iloc[i] < lows.iloc[i-2] and
                    lows.iloc[i] < lows.iloc[i+1] and 
                    lows.iloc[i] < lows.iloc[i+2]):
                    troughs.append((i, lows.iloc[i]))

            if len(troughs) < 2:
                return False

            # Check for double bottom
            for i in range(len(troughs) - 1):
                trough1 = troughs[i]
                trough2 = troughs[i + 1]

                # Troughs should be similar depth
                if abs(trough1[1] - trough2[1]) / trough1[1] < 0.03:
                    return True

            return False

        except Exception as e:
            logger.error(f"Error detecting double bottom: {e}")
            return False

    def _detect_triangle(self, df: pd.DataFrame) -> Optional[Dict]:
        """Detect Triangle patterns"""
        try:
            if len(df) < 20:
                return None

            # Calculate trend lines
            highs = df['high']
            lows = df['low']

            # Simple triangle detection based on converging trend lines
            recent_highs = highs.tail(10)
            recent_lows = lows.tail(10)

            high_trend = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
            low_trend = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]

            # Ascending triangle: horizontal resistance, rising support
            if abs(high_trend) < 0.1 and low_trend > 0.1:
                return {
                    'name': 'Ascending Triangle',
                    'type': 'continuation',
                    'signal': 'bullish',
                    'confidence': 0.6
                }

            # Descending triangle: horizontal support, falling resistance
            if abs(low_trend) < 0.1 and high_trend < -0.1:
                return {
                    'name': 'Descending Triangle',
                    'type': 'continuation',
                    'signal': 'bearish',
                    'confidence': 0.6
                }

            # Symmetrical triangle: converging trend lines
            if abs(high_trend) > 0.1 and abs(low_trend) > 0.1 and np.sign(high_trend) != np.sign(low_trend):
                return {
                    'name': 'Symmetrical Triangle',
                    'type': 'continuation',
                    'signal': 'neutral',
                    'confidence': 0.5
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting triangle: {e}")
            return None

    def _find_support_resistance(self, df: pd.DataFrame) -> List[Dict]:
        """Find support and resistance levels"""
        try:
            if len(df) < 20:
                return []

            levels = []
            highs = df['high']
            lows = df['low']

            # Find significant highs and lows
            for i in range(5, len(df) - 5):
                # Resistance level (significant high)
                if (highs.iloc[i] == highs.iloc[i-5:i+6].max() and
                    highs.iloc[i] > highs.iloc[i-5:i].mean() * 1.02):
                    levels.append({
                        'name': f'Resistance at ${highs.iloc[i]:.2f}',
                        'type': 'resistance',
                        'price': float(highs.iloc[i]),
                        'strength': 'medium'
                    })

                # Support level (significant low)
                if (lows.iloc[i] == lows.iloc[i-5:i+6].min() and
                    lows.iloc[i] < lows.iloc[i-5:i].mean() * 0.98):
                    levels.append({
                        'name': f'Support at ${lows.iloc[i]:.2f}',
                        'type': 'support',
                        'price': float(lows.iloc[i]),
                        'strength': 'medium'
                    })

            return levels[:5]  # Return top 5 levels

        except Exception as e:
            logger.error(f"Error finding support/resistance: {e}")
            return []

    def get_volume_profile(self, symbol: str, days: int = 30) -> Dict:
        """Get volume profile for the chart"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return {"error": "Asset not found"}

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            prices = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            ).order_by(models.Price.timestamp).all()

            if not prices:
                return {"error": "No price data available"}

            # Create volume profile
            volume_profile = {}
            total_volume = 0

            for price in prices:
                # Use the midpoint of high and low as the price level
                price_level = (float(price.high_price) + float(price.low_price)) / 2
                price_level = round(price_level, 2)  # Round to nearest cent
                
                volume = int(price.volume) if price.volume else 0
                
                if price_level in volume_profile:
                    volume_profile[price_level] += volume
                else:
                    volume_profile[price_level] = volume
                
                total_volume += volume

            # Convert to list format for charting
            profile_data = []
            for price_level, volume in sorted(volume_profile.items()):
                percentage = (volume / total_volume) * 100 if total_volume > 0 else 0
                profile_data.append({
                    'price': price_level,
                    'volume': volume,
                    'percentage': round(percentage, 2)
                })

            return {
                'symbol': symbol,
                'volume_profile': profile_data,
                'total_volume': total_volume,
                'price_levels': len(profile_data)
            }

        except Exception as e:
            logger.error(f"Error getting volume profile for {symbol}: {e}")
            return {"error": f"Failed to get volume profile: {str(e)}"}
