from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db import models, schemas
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging
from openai import OpenAI
import os
import json

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)

    def process_chat_message(self, user_id: str, message: str, session_id: Optional[str] = None) -> Dict:
        """Process chat message with ChatGPT"""
        if not self.openai_api_key:
            return {
                "response": "AI service is not configured. Please add your OpenAI API key.",
                "session_id": session_id or "default"
            }
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session_{user_id}_{datetime.utcnow().timestamp()}"
        
        # Get portfolio context
        portfolio_context = self._get_portfolio_context(user_id)
        
        # Prepare context for GPT-5
        context = f"""
        You are Stockee, an AI assistant for a stock and crypto trading simulator. 
        The user has a portfolio with the following information:
        
        {json.dumps(portfolio_context, indent=2)}
        
        Please provide helpful insights about their portfolio, market trends, or trading strategies.
        Keep responses concise and actionable.
        
        User Question: {message}
        """
        
        try:
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=context,
                max_output_tokens=500,
                temperature=0.7,
                timeout=30
            )
            
            ai_response = response.output_text
            
            # Store chat session
            chat_session = models.ChatSession(
                user_id=user_id,
                session_id=session_id,
                message=message,
                response=ai_response,
                context_data=json.dumps(portfolio_context)
            )
            self.db.add(chat_session)
            self.db.commit()
            
            return {
                "response": ai_response,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            
            # More specific error detection
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["quota", "billing", "429", "insufficient_quota", "rate_limit"]):
                return {
                    "response": "🤖 AI Assistant is temporarily unavailable due to API quota limits. Here's what I can tell you about your portfolio:\n\n" + self._get_fallback_portfolio_insights(portfolio_context),
                    "session_id": session_id
                }
            elif "timeout" in error_str or "connection" in error_str:
                return {
                    "response": "⏱️ AI Assistant is experiencing connection issues. Here's your portfolio summary:\n\n" + self._get_fallback_portfolio_insights(portfolio_context),
                    "session_id": session_id
                }
            elif "invalid" in error_str or "unauthorized" in error_str or "401" in error_str:
                return {
                    "response": "🔑 AI Assistant configuration issue. Please check API key settings. Here's your portfolio summary:\n\n" + self._get_fallback_portfolio_insights(portfolio_context),
                    "session_id": session_id
                }
            else:
                return {
                    "response": f"I'm sorry, I encountered an error processing your message: {str(e)[:100]}... Please try again.",
                    "session_id": session_id
                }

    def get_price_predictions(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get AI price predictions for an asset"""
        # Placeholder implementation - in production, use trained ML models
        asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
        if not asset:
            return []
        
        # Get recent prices for trend analysis
        recent_prices = self.db.query(models.Price).filter(
            models.Price.asset_id == asset.id
        ).order_by(desc(models.Price.timestamp)).limit(10).all()
        
        if not recent_prices:
            return []
        
        current_price = recent_prices[0].close_price
        
        # Simple trend-based prediction (replace with actual ML model)
        predictions = []
        for i in range(1, days + 1):
            # Mock prediction with some randomness
            trend_factor = 1 + (i * 0.001)  # Slight upward trend
            predicted_price = current_price * trend_factor * (0.95 + (hash(symbol + str(i)) % 10) * 0.01)
            
            predictions.append({
                "date": (datetime.utcnow() + timedelta(days=i)).isoformat(),
                "predicted_price": round(predicted_price, 2),
                "confidence": 0.7 + (hash(symbol) % 30) * 0.01,
                "model": "trend_analysis_v1"
            })
        
        return predictions

    def get_portfolio_insights(self, user_id: str) -> Dict:
        """Get AI-generated insights for user's portfolio"""
        portfolio_context = self._get_portfolio_context(user_id)
        
        # Simple insights based on portfolio data
        insights = {
            "diversification_score": self._calculate_diversification_score(user_id),
            "risk_level": self._assess_risk_level(user_id),
            "recommendations": self._generate_recommendations(user_id),
            "market_sentiment": "neutral",
            "performance_outlook": "positive"
        }
        
        return insights

    def retrain_models(self) -> Dict:
        """Trigger model retraining"""
        # Placeholder implementation
        return {
            "message": "Model retraining initiated",
            "status": "started",
            "estimated_completion": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }

    def get_model_status(self) -> Dict:
        """Get status of AI models"""
        return {
            "price_prediction": {
                "status": "active",
                "accuracy": 0.75,
                "last_trained": "2024-01-01T00:00:00Z"
            },
            "sentiment_analysis": {
                "status": "active",
                "accuracy": 0.68,
                "last_trained": "2024-01-01T00:00:00Z"
            },
            "portfolio_optimization": {
                "status": "training",
                "accuracy": None,
                "last_trained": None
            }
        }

    def _get_portfolio_context(self, user_id: str) -> Dict:
        """Get portfolio context for AI"""
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        holdings = self.db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio.id
        ).all()
        
        holdings_data = []
        for holding in holdings:
            asset = self.db.query(models.Asset).filter(models.Asset.id == holding.asset_id).first()
            holdings_data.append({
                "symbol": asset.symbol if asset else "Unknown",
                "quantity": holding.quantity,
                "average_cost": holding.average_cost,
                "current_value": holding.current_value
            })
        
        return {
            "cash_balance": portfolio.cash_balance,
            "total_value": portfolio.total_value,
            "holdings": holdings_data,
            "number_of_positions": len(holdings)
        }

    def _calculate_diversification_score(self, user_id: str) -> float:
        """Calculate portfolio diversification score"""
        # Simple implementation
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            return 0.0
        
        holdings = self.db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio.id
        ).all()
        
        if len(holdings) <= 1:
            return 0.3
        elif len(holdings) <= 3:
            return 0.6
        elif len(holdings) <= 5:
            return 0.8
        else:
            return 0.9

    def _assess_risk_level(self, user_id: str) -> str:
        """Assess portfolio risk level"""
        # Simple implementation based on number of holdings
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            return "unknown"
        
        holdings = self.db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio.id
        ).all()
        
        if len(holdings) <= 2:
            return "high"
        elif len(holdings) <= 5:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, user_id: str) -> List[str]:
        """Generate trading recommendations"""
        portfolio_context = self._get_portfolio_context(user_id)
        
        recommendations = []
        
        if portfolio_context.get("number_of_positions", 0) < 3:
            recommendations.append("Consider diversifying your portfolio with more positions")
        
        if portfolio_context.get("cash_balance", 0) > portfolio_context.get("total_value", 1) * 0.5:
            recommendations.append("You have high cash allocation - consider investing more")
        
        if not recommendations:
            recommendations.append("Your portfolio looks well-balanced")
        
        return recommendations

    def _get_fallback_portfolio_insights(self, portfolio_context: Dict) -> str:
        """Generate fallback portfolio insights when AI is unavailable"""
        insights = []
        
        # Portfolio overview
        total_value = portfolio_context.get("total_value", 0)
        cash_balance = portfolio_context.get("cash_balance", 0)
        positions = portfolio_context.get("number_of_positions", 0)
        
        insights.append(f"📊 **Portfolio Overview:**")
        insights.append(f"• Total Value: ${total_value:,.2f}")
        insights.append(f"• Cash Balance: ${cash_balance:,.2f}")
        insights.append(f"• Active Positions: {positions}")
        
        # Top holdings
        holdings = portfolio_context.get("holdings", [])
        if holdings:
            insights.append(f"\n🏆 **Top Holdings:**")
            for i, holding in enumerate(holdings[:3], 1):
                symbol = holding.get("symbol", "N/A")
                value = holding.get("current_value", 0)
                percentage = (value / total_value * 100) if total_value > 0 else 0
                insights.append(f"{i}. {symbol}: ${value:,.2f} ({percentage:.1f}%)")
        
        # Performance summary
        total_return = portfolio_context.get("total_return", 0)
        insights.append(f"\n📈 **Performance:**")
        insights.append(f"• Total Return: {total_return:+.2f}%")
        
        # Recommendations
        recommendations = self._generate_recommendations_from_context(portfolio_context)
        if recommendations:
            insights.append(f"\n💡 **Recommendations:**")
            for rec in recommendations:
                insights.append(f"• {rec}")
        
        insights.append(f"\n⚠️ *Note: AI insights are limited due to API quota. For full AI assistance, please check your OpenAI billing.*")
        
        return "\n".join(insights)

    def _generate_recommendations_from_context(self, portfolio_context: Dict) -> List[str]:
        """Generate recommendations based on portfolio context"""
        recommendations = []
        
        positions = portfolio_context.get("number_of_positions", 0)
        cash_balance = portfolio_context.get("cash_balance", 0)
        total_value = portfolio_context.get("total_value", 1)
        total_return = portfolio_context.get("total_return", 0)
        
        # Diversification
        if positions < 3:
            recommendations.append("Consider diversifying with more positions to reduce risk")
        elif positions > 10:
            recommendations.append("Your portfolio is well-diversified across many positions")
        
        # Cash allocation
        cash_percentage = (cash_balance / total_value) * 100
        if cash_percentage > 50:
            recommendations.append("High cash allocation - consider investing more for better returns")
        elif cash_percentage < 5:
            recommendations.append("Low cash allocation - maintain some liquidity for opportunities")
        
        # Performance
        if total_return > 10:
            recommendations.append("Strong performance! Consider taking some profits")
        elif total_return < -10:
            recommendations.append("Consider reviewing your strategy or rebalancing")
        
        return recommendations[:3]  # Limit to 3 recommendations

    def test_openai_connection(self) -> Dict:
        """Test OpenAI API connection"""
        if not self.openai_api_key:
            return {"status": "error", "message": "No API key configured"}
        
        try:
            response = self.client.responses.create(
                model="gpt-5-mini",
                input="Hello",
                max_output_tokens=10,
                timeout=10
            )
            return {
                "status": "success", 
                "message": "API connection successful",
                "model": "gpt-5-mini",
                "response": response.output_text
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"API connection failed: {str(e)}",
                "error_type": type(e).__name__
            }
