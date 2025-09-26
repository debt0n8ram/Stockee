from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.db import models, schemas
from app.services.portfolio_service import PortfolioService

router = APIRouter()

@router.post("/create", response_model=schemas.Portfolio)
async def create_portfolio(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create a new portfolio for a user"""
    portfolio_service = PortfolioService(db)
    return portfolio_service.create_portfolio(user_id)

@router.get("/{user_id}", response_model=schemas.Portfolio)
async def get_portfolio(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get portfolio by user ID"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_portfolio_by_user_id(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.get("/{user_id}/holdings", response_model=List[schemas.Holding])
async def get_holdings(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all holdings for a portfolio"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_portfolio_by_user_id(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio_service.get_holdings(portfolio.id)

@router.get("/{user_id}/transactions", response_model=List[schemas.Transaction])
async def get_transactions(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get transaction history for a portfolio"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_portfolio_by_user_id(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio_service.get_transactions(portfolio.id, limit)

@router.put("/{user_id}/reset")
async def reset_portfolio(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Reset portfolio to initial state"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_portfolio_by_user_id(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio_service.reset_portfolio(portfolio.id)

@router.get("/{user_id}/performance")
async def get_performance(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get portfolio performance metrics"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_portfolio_by_user_id(user_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio_service.get_performance_metrics(portfolio.id, days)
