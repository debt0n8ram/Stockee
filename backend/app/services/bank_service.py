from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db import models
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class BankService:
    def __init__(self, db: Session):
        self.db = db

    def get_cash_balance(self, user_id: str) -> float:
        """Get current cash balance for a user"""
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            # Create a new portfolio with $10,000 starting balance
            portfolio = models.Portfolio(
                user_id=user_id,
                cash_balance=Decimal('10000.00'),
                total_value=Decimal('10000.00')
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
            
            # Log the initial deposit
            self._log_transaction(
                user_id=user_id,
                transaction_type='deposit',
                amount=Decimal('10000.00'),
                description='Initial deposit',
                balance_after=Decimal('10000.00')
            )
        
        return float(portfolio.cash_balance)

    def deposit_cash(self, user_id: str, amount: float, description: str = "Deposit") -> dict:
        """Deposit cash to user's balance"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            # Create portfolio if it doesn't exist
            portfolio = models.Portfolio(
                user_id=user_id,
                cash_balance=Decimal('0.00'),
                total_value=Decimal('0.00')
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
        
        # Update balance
        old_balance = Decimal(str(portfolio.cash_balance))
        new_balance = old_balance + Decimal(str(amount))
        portfolio.cash_balance = float(new_balance)
        portfolio.total_value = float(new_balance + self._get_invested_value(portfolio.id))
        
        self.db.commit()
        
        # Log transaction
        self._log_transaction(
            user_id=user_id,
            transaction_type='deposit',
            amount=Decimal(str(amount)),
            description=description,
            balance_after=new_balance
        )
        
        return {
            "success": True,
            "message": f"Successfully deposited ${amount:,.2f}",
            "old_balance": float(old_balance),
            "new_balance": float(new_balance),
            "transaction_type": "deposit"
        }

    def withdraw_cash(self, user_id: str, amount: float, description: str = "Withdrawal") -> dict:
        """Withdraw cash from user's balance"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        if Decimal(str(portfolio.cash_balance)) < Decimal(str(amount)):
            raise ValueError("Insufficient funds")
        
        # Update balance
        old_balance = Decimal(str(portfolio.cash_balance))
        new_balance = old_balance - Decimal(str(amount))
        portfolio.cash_balance = float(new_balance)
        portfolio.total_value = float(new_balance + self._get_invested_value(portfolio.id))
        
        self.db.commit()
        
        # Log transaction
        self._log_transaction(
            user_id=user_id,
            transaction_type='withdrawal',
            amount=Decimal(str(amount)),
            description=description,
            balance_after=new_balance
        )
        
        return {
            "success": True,
            "message": f"Successfully withdrew ${amount:,.2f}",
            "old_balance": float(old_balance),
            "new_balance": float(new_balance),
            "transaction_type": "withdrawal"
        }

    def reset_balance(self, user_id: str, new_balance: float) -> dict:
        """Reset user's cash balance to a specific amount"""
        if new_balance < 0:
            raise ValueError("Balance cannot be negative")
        
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            # Create portfolio if it doesn't exist
            portfolio = models.Portfolio(
                user_id=user_id,
                cash_balance=Decimal('0.00'),
                total_value=Decimal('0.00')
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
        
        old_balance = Decimal(str(portfolio.cash_balance))
        portfolio.cash_balance = float(new_balance)
        portfolio.total_value = float(Decimal(str(new_balance)) + self._get_invested_value(portfolio.id))
        
        self.db.commit()
        
        # Log transaction
        self._log_transaction(
            user_id=user_id,
            transaction_type='reset',
            amount=Decimal(str(new_balance)) - old_balance,
            description=f"Balance reset to ${new_balance:,.2f}",
            balance_after=Decimal(str(new_balance))
        )
        
        return {
            "success": True,
            "message": f"Balance reset to ${new_balance:,.2f}",
            "old_balance": float(old_balance),
            "new_balance": float(new_balance),
            "transaction_type": "reset"
        }

    def get_transactions(self, user_id: str, limit: int = 50) -> list:
        """Get bank transaction history for a user"""
        transactions = self.db.query(models.BankTransaction).filter(
            models.BankTransaction.user_id == user_id
        ).order_by(desc(models.BankTransaction.timestamp)).limit(limit).all()
        
        return [
            {
                "id": t.id,
                "user_id": t.user_id,
                "transaction_type": t.transaction_type,
                "amount": float(t.amount),
                "description": t.description,
                "timestamp": t.timestamp,
                "balance_after": float(t.balance_after)
            }
            for t in transactions
        ]

    def _get_invested_value(self, portfolio_id: int) -> Decimal:
        """Calculate the total invested value from holdings"""
        try:
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio_id
            ).all()
            
            total_invested = Decimal('0.0')
            for holding in holdings:
                # Get current price for the asset
                latest_price = self.db.query(models.Price).filter(
                    models.Price.asset_id == holding.asset_id
                ).order_by(models.Price.timestamp.desc()).first()
                
                if latest_price:
                    current_value = Decimal(str(holding.quantity)) * Decimal(str(latest_price.close_price))
                    total_invested += current_value
            
            return total_invested
        except Exception as e:
            logger.error(f"Error calculating invested value: {e}")
            return Decimal('0.0')

    def _log_transaction(self, user_id: str, transaction_type: str, amount: Decimal, 
                        description: str, balance_after: Decimal):
        """Log a bank transaction"""
        transaction = models.BankTransaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            balance_after=balance_after
        )
        self.db.add(transaction)
        self.db.commit()
