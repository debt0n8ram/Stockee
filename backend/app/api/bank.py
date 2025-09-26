from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models, schemas
from app.services.bank_service import BankService
from typing import List

router = APIRouter(prefix="/api/bank", tags=["bank"])

@router.get("/balance/{user_id}")
async def get_cash_balance(user_id: str, db: Session = Depends(get_db)):
    """Get current cash balance for a user"""
    bank_service = BankService(db)
    balance = bank_service.get_cash_balance(user_id)
    return {"user_id": user_id, "cash_balance": balance}

@router.post("/deposit")
async def deposit_cash(
    deposit_request: schemas.DepositRequest,
    db: Session = Depends(get_db)
):
    """Deposit fake money to cash balance"""
    bank_service = BankService(db)
    try:
        result = bank_service.deposit_cash(
            deposit_request.user_id,
            deposit_request.amount,
            deposit_request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/withdraw")
async def withdraw_cash(
    withdraw_request: schemas.WithdrawRequest,
    db: Session = Depends(get_db)
):
    """Withdraw cash from balance (for testing purposes)"""
    bank_service = BankService(db)
    try:
        result = bank_service.withdraw_cash(
            withdraw_request.user_id,
            withdraw_request.amount,
            withdraw_request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/{user_id}")
async def get_bank_transactions(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get bank transaction history"""
    bank_service = BankService(db)
    transactions = bank_service.get_transactions(user_id, limit)
    return {"user_id": user_id, "transactions": transactions}

@router.post("/reset-balance")
async def reset_cash_balance(
    reset_request: schemas.ResetBalanceRequest,
    db: Session = Depends(get_db)
):
    """Reset cash balance to a specific amount"""
    bank_service = BankService(db)
    try:
        result = bank_service.reset_balance(
            reset_request.user_id,
            reset_request.new_balance
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
