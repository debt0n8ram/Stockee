import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_technical_indicators(self, symbol: str, days: int = 30) -> Dict:
        """Calculate technical indicators for a symbol"""
        try:
            # Get historical data
            historical_data = self._get_historical_data(symbol, days)
            if not historical_data or len(historical_data) < 14:
                return {"error": "Insufficient data for technical analysis"}
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate indicators
            indicators = {}
            
            # Moving Averages
            indicators['moving_averages'] = self._calculate_moving_averages(df)
            
            # RSI
            indicators['rsi'] = self._calculate_rsi(df)
            
            # MACD
            indicators['macd'] = self._calculate_macd(df)
            
            # Bollinger Bands
            indicators['bollinger_bands'] = self._calculate_bollinger_bands(df)
            
            # Stochastic Oscillator
            indicators['stochastic'] = self._calculate_stochastic(df)
            
            # Williams %R
            indicators['williams_r'] = self._calculate_williams_r(df)
            
            # Commodity Channel Index (CCI)
            indicators['cci'] = self._calculate_cci(df)
            
            # Average True Range (ATR)
            indicators['atr'] = self._calculate_atr(df)
            
            # Volume indicators
            indicators['volume_indicators'] = self._calculate_volume_indicators(df)
            
            # Support and Resistance
            indicators['support_resistance'] = self._calculate_support_resistance(df)
            
            # Trend analysis
            indicators['trend_analysis'] = self._analyze_trend(df)
            
            # Price patterns
            indicators['price_patterns'] = self._analyze_price_patterns(df)
            
            return {
                'symbol': symbol,
                'indicators': indicators,
                'last_updated': datetime.now().isoformat(),
                'data_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return {"error": f"Failed to calculate indicators: {str(e)}"}

    def _get_historical_data(self, symbol: str, days: int) -> List[Dict]:
        """Get historical price data for a symbol"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return []
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            prices = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            ).order_by(models.Price.timestamp).all()
            
            return [
                {
                    'date': price.timestamp.strftime('%Y-%m-%d'),
                    'open': float(price.open_price),
                    'high': float(price.high_price),
                    'low': float(price.low_price),
                    'close': float(price.close_price),
                    'volume': int(price.volume) if price.volume else 0
                }
                for price in prices
            ]
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []

    def _calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """Calculate various moving averages"""
        try:
            closes = df['close']
            
            return {
                'sma_5': float(closes.rolling(window=5).mean().iloc[-1]) if len(closes) >= 5 else None,
                'sma_10': float(closes.rolling(window=10).mean().iloc[-1]) if len(closes) >= 10 else None,
                'sma_20': float(closes.rolling(window=20).mean().iloc[-1]) if len(closes) >= 20 else None,
                'sma_50': float(closes.rolling(window=50).mean().iloc[-1]) if len(closes) >= 50 else None,
                'ema_12': float(closes.ewm(span=12).mean().iloc[-1]) if len(closes) >= 12 else None,
                'ema_26': float(closes.ewm(span=26).mean().iloc[-1]) if len(closes) >= 26 else None,
                'current_price': float(closes.iloc[-1])
            }
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return {}

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """Calculate RSI (Relative Strength Index)"""
        try:
            closes = df['close']
            delta = closes.diff()
            
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
            
            # RSI interpretation
            interpretation = "Neutral"
            if current_rsi:
                if current_rsi > 70:
                    interpretation = "Overbought"
                elif current_rsi < 30:
                    interpretation = "Oversold"
                elif current_rsi > 50:
                    interpretation = "Bullish"
                else:
                    interpretation = "Bearish"
            
            return {
                'current_rsi': current_rsi,
                'interpretation': interpretation,
                'overbought_threshold': 70,
                'oversold_threshold': 30
            }
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return {}

    def _calculate_macd(self, df: pd.DataFrame) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            closes = df['close']
            
            ema_12 = closes.ewm(span=12).mean()
            ema_26 = closes.ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            current_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None
            current_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None
            current_histogram = float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None
            
            # MACD interpretation
            interpretation = "Neutral"
            if current_macd and current_signal:
                if current_macd > current_signal:
                    interpretation = "Bullish"
                else:
                    interpretation = "Bearish"
            
            return {
                'macd_line': current_macd,
                'signal_line': current_signal,
                'histogram': current_histogram,
                'interpretation': interpretation
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {}

    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> Dict:
        """Calculate Bollinger Bands"""
        try:
            closes = df['close']
            sma = closes.rolling(window=period).mean()
            std = closes.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            current_price = float(closes.iloc[-1])
            current_upper = float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else None
            current_lower = float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else None
            current_middle = float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None
            
            # Bollinger Bands interpretation
            interpretation = "Neutral"
            if current_upper and current_lower and current_middle:
                if current_price > current_upper:
                    interpretation = "Overbought"
                elif current_price < current_lower:
                    interpretation = "Oversold"
                elif current_price > current_middle:
                    interpretation = "Bullish"
                else:
                    interpretation = "Bearish"
            
            return {
                'upper_band': current_upper,
                'middle_band': current_middle,
                'lower_band': current_lower,
                'current_price': current_price,
                'interpretation': interpretation,
                'bandwidth': float((current_upper - current_lower) / current_middle * 100) if current_upper and current_lower and current_middle else None
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {}

    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict:
        """Calculate Stochastic Oscillator"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            current_k = float(k_percent.iloc[-1]) if not pd.isna(k_percent.iloc[-1]) else None
            current_d = float(d_percent.iloc[-1]) if not pd.isna(d_percent.iloc[-1]) else None
            
            # Stochastic interpretation
            interpretation = "Neutral"
            if current_k and current_d:
                if current_k > 80 and current_d > 80:
                    interpretation = "Overbought"
                elif current_k < 20 and current_d < 20:
                    interpretation = "Oversold"
                elif current_k > current_d:
                    interpretation = "Bullish"
                else:
                    interpretation = "Bearish"
            
            return {
                'k_percent': current_k,
                'd_percent': current_d,
                'interpretation': interpretation,
                'overbought_threshold': 80,
                'oversold_threshold': 20
            }
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return {}

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate volume-based indicators"""
        try:
            volume = df['volume']
            close = df['close']
            
            # Volume moving average
            volume_sma = volume.rolling(window=20).mean()
            current_volume = int(volume.iloc[-1]) if not pd.isna(volume.iloc[-1]) else 0
            avg_volume = float(volume_sma.iloc[-1]) if not pd.isna(volume_sma.iloc[-1]) else 0
            
            # Volume trend
            volume_trend = "Neutral"
            if current_volume > avg_volume * 1.5:
                volume_trend = "High"
            elif current_volume < avg_volume * 0.5:
                volume_trend = "Low"
            
            # Price-Volume trend
            price_change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100 if len(close) > 1 else 0
            volume_change = (current_volume - avg_volume) / avg_volume * 100 if avg_volume > 0 else 0
            
            return {
                'current_volume': current_volume,
                'average_volume': avg_volume,
                'volume_trend': volume_trend,
                'volume_ratio': float(current_volume / avg_volume) if avg_volume > 0 else 0,
                'price_change': float(price_change),
                'volume_change': float(volume_change)
            }
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {e}")
            return {}

    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Calculate support and resistance levels"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # Simple support and resistance calculation
            recent_highs = high.tail(20)
            recent_lows = low.tail(20)
            
            resistance = float(recent_highs.max()) if len(recent_highs) > 0 else None
            support = float(recent_lows.min()) if len(recent_lows) > 0 else None
            current_price = float(close.iloc[-1])
            
            # Calculate distance to support/resistance
            resistance_distance = float((resistance - current_price) / current_price * 100) if resistance else None
            support_distance = float((current_price - support) / current_price * 100) if support else None
            
            return {
                'resistance': resistance,
                'support': support,
                'current_price': current_price,
                'resistance_distance': resistance_distance,
                'support_distance': support_distance
            }
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {}

    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Analyze overall trend"""
        try:
            close = df['close']
            
            # Short-term trend (5 days)
            short_trend = "Neutral"
            if len(close) >= 5:
                short_change = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100
                if short_change > 2:
                    short_trend = "Bullish"
                elif short_change < -2:
                    short_trend = "Bearish"
            
            # Medium-term trend (20 days)
            medium_trend = "Neutral"
            if len(close) >= 20:
                medium_change = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] * 100
                if medium_change > 5:
                    medium_trend = "Bullish"
                elif medium_change < -5:
                    medium_trend = "Bearish"
            
            # Trend strength
            trend_strength = "Weak"
            if abs(short_change) > 5 or abs(medium_change) > 10:
                trend_strength = "Strong"
            elif abs(short_change) > 2 or abs(medium_change) > 5:
                trend_strength = "Moderate"
            
            return {
                'short_term_trend': short_trend,
                'medium_term_trend': medium_trend,
                'trend_strength': trend_strength,
                'short_term_change': float(short_change) if len(close) >= 5 else 0,
                'medium_term_change': float(medium_change) if len(close) >= 20 else 0
            }
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {}

    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """Calculate Williams %R"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            
            current_williams_r = float(williams_r.iloc[-1]) if not pd.isna(williams_r.iloc[-1]) else None
            
            # Williams %R interpretation
            interpretation = "Neutral"
            if current_williams_r:
                if current_williams_r > -20:
                    interpretation = "Overbought"
                elif current_williams_r < -80:
                    interpretation = "Oversold"
                elif current_williams_r > -50:
                    interpretation = "Bullish"
                else:
                    interpretation = "Bearish"
            
            return {
                'current_williams_r': current_williams_r,
                'interpretation': interpretation,
                'overbought_threshold': -20,
                'oversold_threshold': -80
            }
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return {}

    def _calculate_cci(self, df: pd.DataFrame, period: int = 20) -> Dict:
        """Calculate Commodity Channel Index (CCI)"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # Typical Price
            typical_price = (high + low + close) / 3
            
            # Simple Moving Average of Typical Price
            sma_tp = typical_price.rolling(window=period).mean()
            
            # Mean Deviation
            mean_deviation = typical_price.rolling(window=period).apply(
                lambda x: np.mean(np.abs(x - x.mean()))
            )
            
            # CCI Calculation
            cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
            
            current_cci = float(cci.iloc[-1]) if not pd.isna(cci.iloc[-1]) else None
            
            # CCI interpretation
            interpretation = "Neutral"
            if current_cci:
                if current_cci > 100:
                    interpretation = "Overbought"
                elif current_cci < -100:
                    interpretation = "Oversold"
                elif current_cci > 0:
                    interpretation = "Bullish"
                else:
                    interpretation = "Bearish"
            
            return {
                'current_cci': current_cci,
                'interpretation': interpretation,
                'overbought_threshold': 100,
                'oversold_threshold': -100
            }
        except Exception as e:
            logger.error(f"Error calculating CCI: {e}")
            return {}

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """Calculate Average True Range (ATR)"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR calculation
            atr = true_range.rolling(window=period).mean()
            
            current_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None
            current_price = float(close.iloc[-1])
            
            # ATR interpretation
            volatility_level = "Normal"
            if current_atr and current_price:
                atr_percentage = (current_atr / current_price) * 100
                if atr_percentage > 5:
                    volatility_level = "High"
                elif atr_percentage < 2:
                    volatility_level = "Low"
            
            return {
                'current_atr': current_atr,
                'atr_percentage': float((current_atr / current_price) * 100) if current_atr and current_price else None,
                'volatility_level': volatility_level,
                'current_price': current_price
            }
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return {}

    def _analyze_price_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze basic price patterns"""
        try:
            close = df['close']
            high = df['high']
            low = df['low']
            
            if len(close) < 5:
                return {"patterns": [], "trend_strength": "Insufficient data"}
            
            patterns = []
            trend_strength = "Weak"
            
            # Recent price action
            recent_closes = close.tail(5)
            recent_highs = high.tail(5)
            recent_lows = low.tail(5)
            
            # Check for higher highs and higher lows (uptrend)
            if len(recent_highs) >= 3 and len(recent_lows) >= 3:
                if (recent_highs.iloc[-1] > recent_highs.iloc[-2] > recent_highs.iloc[-3] and
                    recent_lows.iloc[-1] > recent_lows.iloc[-2] > recent_lows.iloc[-3]):
                    patterns.append("Higher Highs and Higher Lows")
                    trend_strength = "Strong"
                elif (recent_highs.iloc[-1] > recent_highs.iloc[-2] or
                      recent_lows.iloc[-1] > recent_lows.iloc[-2]):
                    patterns.append("Potential Uptrend")
                    trend_strength = "Moderate"
            
            # Check for lower highs and lower lows (downtrend)
            if len(recent_highs) >= 3 and len(recent_lows) >= 3:
                if (recent_highs.iloc[-1] < recent_highs.iloc[-2] < recent_highs.iloc[-3] and
                    recent_lows.iloc[-1] < recent_lows.iloc[-2] < recent_lows.iloc[-3]):
                    patterns.append("Lower Highs and Lower Lows")
                    trend_strength = "Strong"
                elif (recent_highs.iloc[-1] < recent_highs.iloc[-2] or
                      recent_lows.iloc[-1] < recent_lows.iloc[-2]):
                    patterns.append("Potential Downtrend")
                    trend_strength = "Moderate"
            
            # Check for consolidation
            if len(recent_closes) >= 5:
                price_range = recent_closes.max() - recent_closes.min()
                avg_price = recent_closes.mean()
                if price_range / avg_price < 0.02:  # Less than 2% range
                    patterns.append("Consolidation")
                    trend_strength = "Weak"
            
            # Check for breakout
            if len(close) >= 20:
                recent_high = recent_highs.max()
                previous_high = high.iloc[-20:-5].max()
                if recent_high > previous_high * 1.02:  # 2% breakout
                    patterns.append("Breakout")
                    trend_strength = "Strong"
            
            return {
                "patterns": patterns,
                "trend_strength": trend_strength,
                "recent_high": float(recent_highs.max()) if len(recent_highs) > 0 else None,
                "recent_low": float(recent_lows.min()) if len(recent_lows) > 0 else None
            }
        except Exception as e:
            logger.error(f"Error analyzing price patterns: {e}")
            return {"patterns": [], "trend_strength": "Error"}
