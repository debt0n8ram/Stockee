import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.db import models
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class MarketScreenerService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)

    def screen_stocks(self, filters: Dict) -> List[Dict]:
        """Screen stocks based on various criteria"""
        try:
            query = self.db.query(models.Asset).filter(models.Asset.asset_type == 'stock')
            
            # Apply filters
            if filters.get('min_price'):
                query = query.join(models.Price).filter(
                    models.Price.close_price >= filters['min_price']
                )
            
            if filters.get('max_price'):
                query = query.join(models.Price).filter(
                    models.Price.close_price <= filters['max_price']
                )
            
            if filters.get('min_volume'):
                query = query.join(models.Price).filter(
                    models.Price.volume >= filters['min_volume']
                )
            
            if filters.get('exchange'):
                query = query.filter(models.Asset.exchange == filters['exchange'])
            
            if filters.get('sector'):
                query = query.filter(models.Asset.sector == filters['sector'])
            
            # Get results
            assets = query.limit(filters.get('limit', 50)).all()
            
            # Enhance with current data
            results = []
            for asset in assets:
                try:
                    current_price = self.market_data_service.get_current_price(asset.symbol)
                    if current_price:
                        results.append({
                            'symbol': asset.symbol,
                            'name': asset.name,
                            'exchange': asset.exchange,
                            'sector': asset.sector,
                            'current_price': current_price['price'],
                            'change': current_price.get('change', 0),
                            'change_percent': current_price.get('change_percent', 0),
                            'volume': current_price.get('volume', 0),
                            'market_cap': current_price.get('market_cap', 0)
                        })
                except Exception as e:
                    logger.error(f"Error getting current price for {asset.symbol}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error screening stocks: {e}")
            return []

    def get_top_gainers(self, limit: int = 20) -> List[Dict]:
        """Get top gaining stocks"""
        try:
            # Get recent price data
            recent_prices = self.db.query(models.Price).join(models.Asset).filter(
                models.Asset.asset_type == 'stock'
            ).order_by(models.Price.timestamp.desc()).limit(1000).all()
            
            # Calculate gains
            gainers = []
            for price in recent_prices:
                try:
                    # Get previous price for comparison
                    previous_price = self.db.query(models.Price).filter(
                        models.Price.asset_id == price.asset_id,
                        models.Price.timestamp < price.timestamp
                    ).order_by(models.Price.timestamp.desc()).first()
                    
                    if previous_price:
                        change = price.close_price - previous_price.close_price
                        change_percent = (change / previous_price.close_price) * 100
                        
                        if change_percent > 0:  # Only gainers
                            gainers.append({
                                'symbol': price.asset.symbol,
                                'name': price.asset.name,
                                'current_price': float(price.close_price),
                                'change': float(change),
                                'change_percent': float(change_percent),
                                'volume': int(price.volume) if price.volume else 0
                            })
                except Exception as e:
                    logger.error(f"Error calculating gain for {price.asset.symbol}: {e}")
                    continue
            
            # Sort by change percentage and return top gainers
            gainers.sort(key=lambda x: x['change_percent'], reverse=True)
            return gainers[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top gainers: {e}")
            return []

    def get_top_losers(self, limit: int = 20) -> List[Dict]:
        """Get top losing stocks"""
        try:
            # Get recent price data
            recent_prices = self.db.query(models.Price).join(models.Asset).filter(
                models.Asset.asset_type == 'stock'
            ).order_by(models.Price.timestamp.desc()).limit(1000).all()
            
            # Calculate losses
            losers = []
            for price in recent_prices:
                try:
                    # Get previous price for comparison
                    previous_price = self.db.query(models.Price).filter(
                        models.Price.asset_id == price.asset_id,
                        models.Price.timestamp < price.timestamp
                    ).order_by(models.Price.timestamp.desc()).first()
                    
                    if previous_price:
                        change = price.close_price - previous_price.close_price
                        change_percent = (change / previous_price.close_price) * 100
                        
                        if change_percent < 0:  # Only losers
                            losers.append({
                                'symbol': price.asset.symbol,
                                'name': price.asset.name,
                                'current_price': float(price.close_price),
                                'change': float(change),
                                'change_percent': float(change_percent),
                                'volume': int(price.volume) if price.volume else 0
                            })
                except Exception as e:
                    logger.error(f"Error calculating loss for {price.asset.symbol}: {e}")
                    continue
            
            # Sort by change percentage (most negative first) and return top losers
            losers.sort(key=lambda x: x['change_percent'])
            return losers[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top losers: {e}")
            return []

    def get_most_active(self, limit: int = 20) -> List[Dict]:
        """Get most actively traded stocks"""
        try:
            # Get recent price data ordered by volume
            recent_prices = self.db.query(models.Price).join(models.Asset).filter(
                models.Asset.asset_type == 'stock',
                models.Price.volume.isnot(None)
            ).order_by(models.Price.timestamp.desc(), models.Price.volume.desc()).limit(limit).all()
            
            most_active = []
            for price in recent_prices:
                try:
                    most_active.append({
                        'symbol': price.asset.symbol,
                        'name': price.asset.name,
                        'current_price': float(price.close_price),
                        'volume': int(price.volume) if price.volume else 0,
                        'change': 0,  # Would need to calculate
                        'change_percent': 0  # Would need to calculate
                    })
                except Exception as e:
                    logger.error(f"Error processing most active for {price.asset.symbol}: {e}")
                    continue
            
            return most_active
            
        except Exception as e:
            logger.error(f"Error getting most active stocks: {e}")
            return []

    def get_sector_performance(self) -> List[Dict]:
        """Get performance by sector"""
        try:
            # Get all stocks with their sectors
            stocks = self.db.query(models.Asset).filter(
                models.Asset.asset_type == 'stock',
                models.Asset.sector.isnot(None)
            ).all()
            
            sector_data = {}
            
            for stock in stocks:
                try:
                    current_price = self.market_data_service.get_current_price(stock.symbol)
                    if current_price and stock.sector:
                        if stock.sector not in sector_data:
                            sector_data[stock.sector] = {
                                'sector': stock.sector,
                                'stocks': 0,
                                'total_change': 0,
                                'avg_change': 0
                            }
                        
                        sector_data[stock.sector]['stocks'] += 1
                        sector_data[stock.sector]['total_change'] += current_price.get('change_percent', 0)
                except Exception as e:
                    logger.error(f"Error processing sector data for {stock.symbol}: {e}")
                    continue
            
            # Calculate average change per sector
            for sector in sector_data:
                if sector_data[sector]['stocks'] > 0:
                    sector_data[sector]['avg_change'] = (
                        sector_data[sector]['total_change'] / sector_data[sector]['stocks']
                    )
            
            # Convert to list and sort by average change
            sector_performance = list(sector_data.values())
            sector_performance.sort(key=lambda x: x['avg_change'], reverse=True)
            
            return sector_performance
            
        except Exception as e:
            logger.error(f"Error getting sector performance: {e}")
            return []

    def get_market_overview(self) -> Dict:
        """Get overall market overview"""
        try:
            # Get market statistics
            total_stocks = self.db.query(models.Asset).filter(
                models.Asset.asset_type == 'stock'
            ).count()
            
            # Get recent price data
            recent_prices = self.db.query(models.Price).join(models.Asset).filter(
                models.Asset.asset_type == 'stock'
            ).order_by(models.Price.timestamp.desc()).limit(1000).all()
            
            # Calculate market statistics
            total_volume = 0
            advancing_stocks = 0
            declining_stocks = 0
            unchanged_stocks = 0
            
            for price in recent_prices:
                try:
                    if price.volume:
                        total_volume += int(price.volume)
                    
                    # Get previous price for comparison
                    previous_price = self.db.query(models.Price).filter(
                        models.Price.asset_id == price.asset_id,
                        models.Price.timestamp < price.timestamp
                    ).order_by(models.Price.timestamp.desc()).first()
                    
                    if previous_price:
                        change_percent = ((price.close_price - previous_price.close_price) / previous_price.close_price) * 100
                        
                        if change_percent > 0:
                            advancing_stocks += 1
                        elif change_percent < 0:
                            declining_stocks += 1
                        else:
                            unchanged_stocks += 1
                            
                except Exception as e:
                    logger.error(f"Error processing market overview for {price.asset.symbol}: {e}")
                    continue
            
            return {
                'total_stocks': total_stocks,
                'total_volume': total_volume,
                'advancing_stocks': advancing_stocks,
                'declining_stocks': declining_stocks,
                'unchanged_stocks': unchanged_stocks,
                'advance_decline_ratio': (
                    advancing_stocks / declining_stocks if declining_stocks > 0 else 0
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {}
