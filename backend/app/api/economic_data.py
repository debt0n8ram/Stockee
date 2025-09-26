"""
Economic Data API Endpoints
Provides economic indicators and macro data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.economic_data_service import EconomicDataService
from typing import Optional

router = APIRouter(prefix="/api/economic", tags=["economic-data"])

# Initialize service
economic_service = EconomicDataService()

@router.get("/indicators")
async def get_economic_indicators(db: Session = Depends(get_db)):
    """Get comprehensive economic indicators from FRED, World Bank, and IMF"""
    try:
        return await economic_service.get_economic_indicators()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fed-rates")
async def get_fed_rates(db: Session = Depends(get_db)):
    """Get Federal Reserve interest rates"""
    try:
        indicators = await economic_service.get_economic_indicators()
        fed_data = indicators.get("indicators", {}).get("fred", {})
        
        return {
            "fed_funds_rate": fed_data.get("FEDFUNDS", {}),
            "treasury_10y": fed_data.get("DGS10", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inflation")
async def get_inflation_data(db: Session = Depends(get_db)):
    """Get inflation indicators"""
    try:
        indicators = await economic_service.get_economic_indicators()
        fred_data = indicators.get("indicators", {}).get("fred", {})
        
        return {
            "cpi": fred_data.get("CPIAUCSL", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unemployment")
async def get_unemployment_data(db: Session = Depends(get_db)):
    """Get unemployment data"""
    try:
        indicators = await economic_service.get_economic_indicators()
        fred_data = indicators.get("indicators", {}).get("fred", {})
        
        return {
            "unemployment_rate": fred_data.get("UNRATE", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
