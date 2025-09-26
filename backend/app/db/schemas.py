from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# Asset schemas
class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: str
    exchange: Optional[str] = None
    currency: str = "USD"
    sector: Optional[str] = None
    market_cap: Optional[float] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Price schemas
class PriceBase(BaseModel):
    asset_id: int
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    adjusted_close: Optional[float] = None

class PriceCreate(PriceBase):
    pass

class Price(PriceBase):
    id: int
    
    class Config:
        from_attributes = True

# Portfolio schemas
class PortfolioBase(BaseModel):
    user_id: str
    cash_balance: float = 100000.0

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    total_value: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Holding schemas
class HoldingBase(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float
    average_cost: float

class HoldingCreate(HoldingBase):
    pass

class Holding(HoldingBase):
    id: int
    current_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    asset: Optional[Asset] = None
    
    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    portfolio_id: int
    asset_id: int
    transaction_type: str
    quantity: float
    price: float
    total_amount: float
    fees: float = 0.0
    order_type: str = "market"

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    asset: Optional[Asset] = None
    
    class Config:
        from_attributes = True

# Analytics schemas
class AnalyticsBase(BaseModel):
    portfolio_id: int
    date: datetime
    total_value: float
    daily_return: Optional[float] = None
    cumulative_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    volatility: Optional[float] = None
    beta: Optional[float] = None

class AnalyticsCreate(AnalyticsBase):
    pass

class Analytics(AnalyticsBase):
    id: int
    
    class Config:
        from_attributes = True

# AI Prediction schemas
class AIPredictionBase(BaseModel):
    asset_id: int
    model_name: str
    prediction_date: datetime
    target_date: datetime
    predicted_price: float
    confidence: Optional[float] = None
    model_version: Optional[str] = None

class AIPredictionCreate(AIPredictionBase):
    pass

# Bank schemas
class DepositRequest(BaseModel):
    user_id: str
    amount: float
    description: Optional[str] = "Deposit"

class WithdrawRequest(BaseModel):
    user_id: str
    amount: float
    description: Optional[str] = "Withdrawal"

class ResetBalanceRequest(BaseModel):
    user_id: str
    new_balance: float

class BankTransaction(BaseModel):
    id: int
    user_id: str
    transaction_type: str
    amount: float
    description: str
    timestamp: datetime
    balance_after: float

    class Config:
        from_attributes = True

class AIPrediction(AIPredictionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatMessage(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime

# Trading schemas
class TradeOrder(BaseModel):
    symbol: str
    quantity: float
    order_type: str = "market"  # market, limit, stop
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None

class TradeRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: float
    order_type: str = "market"  # market, limit, stop
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None

class TradeResponse(BaseModel):
    success: bool
    message: str
    transaction_id: Optional[int] = None
    order_id: Optional[str] = None

# AI Opponent schemas
class AIOpponentBase(BaseModel):
    user_id: str
    strategy_type: str

class AIOpponentCreate(AIOpponentBase):
    pass

class AIOpponent(AIOpponentBase):
    id: int
    ai_user_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    total_trades: int
    winning_trades: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CompetitionData(BaseModel):
    user_performance: Dict[str, Any]
    ai_performance: Dict[str, Any]
    competition: Dict[str, Any]
    ai_opponent_id: int
