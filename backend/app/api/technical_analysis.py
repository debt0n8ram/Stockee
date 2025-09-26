from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.technical_analysis_service import TechnicalAnalysisService
from typing import Dict

router = APIRouter(prefix="/api/technical", tags=["technical-analysis"])

@router.get("/indicators/{symbol}")
async def get_technical_indicators(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get technical indicators for a stock symbol"""
    technical_service = TechnicalAnalysisService(db)
    indicators = technical_service.calculate_technical_indicators(symbol.upper(), days)
    
    if "error" in indicators:
        raise HTTPException(status_code=400, detail=indicators["error"])
    
    return indicators

@router.get("/indicators/{symbol}/summary")
async def get_technical_summary(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get a summary of technical indicators with interpretations"""
    technical_service = TechnicalAnalysisService(db)
    indicators = technical_service.calculate_technical_indicators(symbol.upper(), days)
    
    if "error" in indicators:
        raise HTTPException(status_code=400, detail=indicators["error"])
    
    # Create a summary with key insights
    summary = {
        "symbol": symbol.upper(),
        "overall_sentiment": "Neutral",
        "key_insights": [],
        "recommendations": [],
        "risk_level": "Medium"
    }
    
    try:
        indicators_data = indicators.get("indicators", {})
        
        # Analyze RSI
        rsi = indicators_data.get("rsi", {})
        if rsi.get("current_rsi"):
            if rsi["current_rsi"] > 70:
                summary["key_insights"].append("RSI indicates overbought conditions")
                summary["recommendations"].append("Consider taking profits or waiting for pullback")
            elif rsi["current_rsi"] < 30:
                summary["key_insights"].append("RSI indicates oversold conditions")
                summary["recommendations"].append("Potential buying opportunity")
        
        # Analyze MACD
        macd = indicators_data.get("macd", {})
        if macd.get("interpretation"):
            summary["key_insights"].append(f"MACD shows {macd['interpretation'].lower()} momentum")
        
        # Analyze trend
        trend = indicators_data.get("trend_analysis", {})
        if trend.get("trend_strength"):
            summary["key_insights"].append(f"Trend strength: {trend['trend_strength']}")
            if trend["trend_strength"] == "Strong":
                summary["risk_level"] = "High"
            elif trend["trend_strength"] == "Weak":
                summary["risk_level"] = "Low"
        
        # Analyze volume
        volume = indicators_data.get("volume_indicators", {})
        if volume.get("volume_trend"):
            if volume["volume_trend"] == "High":
                summary["key_insights"].append("High volume confirms price movement")
            elif volume["volume_trend"] == "Low":
                summary["key_insights"].append("Low volume suggests weak conviction")
        
        # Determine overall sentiment
        bullish_signals = 0
        bearish_signals = 0
        
        if rsi.get("interpretation") == "Oversold":
            bullish_signals += 1
        elif rsi.get("interpretation") == "Overbought":
            bearish_signals += 1
            
        if macd.get("interpretation") == "Bullish":
            bullish_signals += 1
        elif macd.get("interpretation") == "Bearish":
            bearish_signals += 1
            
        if trend.get("short_term_trend") == "Bullish":
            bullish_signals += 1
        elif trend.get("short_term_trend") == "Bearish":
            bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            summary["overall_sentiment"] = "Bullish"
        elif bearish_signals > bullish_signals:
            summary["overall_sentiment"] = "Bearish"
        
        # Add general recommendations
        if summary["overall_sentiment"] == "Bullish":
            summary["recommendations"].append("Consider long positions with proper risk management")
        elif summary["overall_sentiment"] == "Bearish":
            summary["recommendations"].append("Consider short positions or wait for better entry")
        else:
            summary["recommendations"].append("Wait for clearer signals before making decisions")
        
    except Exception as e:
        summary["key_insights"].append("Unable to generate detailed analysis")
    
    return {
        "summary": summary,
        "detailed_indicators": indicators
    }
