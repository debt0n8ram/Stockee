from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db import models, schemas
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TradingService:
    def __init__(self, db: Session):
        self.db = db

    def execute_buy_order(self, user_id: str, symbol: str, quantity: float, price: float, order_type: str = "market") -> Dict:
        """Execute a buy order"""
        # Get or create portfolio
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            portfolio = models.Portfolio(user_id=user_id, cash_balance=100000.0, total_value=100000.0)
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
        
        # Get or create asset
        asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
        if not asset:
            # Try to get asset info from market data service
            from app.services.market_data_service import MarketDataService
            market_service = MarketDataService(self.db)
            
            # Try to get asset info from search
            search_results = market_service.search_assets(symbol, limit=1)
            asset_name = f"{symbol} Stock"  # Default name
            
            if search_results and len(search_results) > 0:
                asset_name = search_results[0].get('name', f"{symbol} Stock")
            
            asset = models.Asset(
                symbol=symbol,
                name=asset_name,
                asset_type="stock",
                currency="USD"
            )
            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)
        
        # Calculate total cost
        total_cost = quantity * price
        fees = total_cost * 0.001  # 0.1% fee
        total_with_fees = total_cost + fees
        
        # Check if user has enough cash
        if portfolio.cash_balance < total_with_fees:
            raise ValueError(f"Insufficient funds. Required: ${total_with_fees:.2f}, Available: ${portfolio.cash_balance:.2f}")
        
        # Create transaction
        transaction = models.Transaction(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            transaction_type="buy",
            quantity=quantity,
            price=price,
            total_amount=total_cost,
            fees=fees,
            order_type=order_type
        )
        self.db.add(transaction)
        
        # Update portfolio cash balance
        portfolio.cash_balance -= total_with_fees
        
        # Update or create holding
        holding = self.db.query(models.Holding).filter(
            and_(
                models.Holding.portfolio_id == portfolio.id,
                models.Holding.asset_id == asset.id
            )
        ).first()
        
        if holding:
            # Update existing holding
            total_quantity = holding.quantity + quantity
            total_cost_basis = (holding.quantity * holding.average_cost) + total_cost
            new_average_cost = total_cost_basis / total_quantity
            
            holding.quantity = total_quantity
            holding.average_cost = new_average_cost
        else:
            # Create new holding
            holding = models.Holding(
                portfolio_id=portfolio.id,
                asset_id=asset.id,
                quantity=quantity,
                average_cost=price
            )
            self.db.add(holding)
        
        self.db.commit()
        
        return {
            "transaction_id": transaction.id,
            "message": f"Successfully bought {quantity} shares of {symbol} at ${price:.2f}"
        }

    def execute_sell_order(self, user_id: str, symbol: str, quantity: float, price: float, order_type: str = "market") -> Dict:
        """Execute a sell order"""
        # Get portfolio
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Get asset
        asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
        if not asset:
            raise ValueError(f"Asset {symbol} not found")
        
        # Get holding
        holding = self.db.query(models.Holding).filter(
            and_(
                models.Holding.portfolio_id == portfolio.id,
                models.Holding.asset_id == asset.id
            )
        ).first()
        
        if not holding:
            raise ValueError(f"No holdings found for {symbol}")
        
        if holding.quantity < quantity:
            raise ValueError(f"Insufficient shares. Available: {holding.quantity}, Requested: {quantity}")
        
        # Calculate proceeds
        proceeds = quantity * price
        fees = proceeds * 0.001  # 0.1% fee
        net_proceeds = proceeds - fees
        
        # Create transaction
        transaction = models.Transaction(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            transaction_type="sell",
            quantity=quantity,
            price=price,
            total_amount=proceeds,
            fees=fees,
            order_type=order_type
        )
        self.db.add(transaction)
        
        # Update portfolio cash balance
        portfolio.cash_balance += net_proceeds
        
        # Update holding
        holding.quantity -= quantity
        
        # Remove holding if quantity becomes zero
        if holding.quantity <= 0:
            self.db.delete(holding)
        
        self.db.commit()
        
        return {
            "transaction_id": transaction.id,
            "message": f"Successfully sold {quantity} shares of {symbol} at ${price:.2f}"
        }

    def get_open_orders(self, user_id: str) -> List[Dict]:
        """Get open orders for a user (placeholder - implement order management)"""
        return []

    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an open order (placeholder)"""
        return {"message": "Order cancelled successfully"}
