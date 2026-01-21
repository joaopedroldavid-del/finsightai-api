from pydantic_ai.tools import Tool
from typing import List, Dict, Any
import logging
from app.agents.tools.factory import ToolFactory

logger = logging.getLogger(__name__)

class AgentTools:
    """
    Tool wrappers for PydanticAI agent integration
    """

    def __init__(self):
        self.tool_factory = ToolFactory()
        logger.info("✅ AgentTools initialized")

    # Static method for price analysis implementation
    @staticmethod
    async def _get_price_analysis_impl(symbol: str, period: str = "1month") -> Dict[str, Any]:
        """Internal implementation - static method"""
        logger.info(f"🔧 Price analysis implementation: {symbol}, {period}")
        try:
            # Create tool factory instance inside the static method
            tool_factory = ToolFactory()
            price_tool = tool_factory.get_price_tool()
            result = await price_tool.get_price_data(symbol, period)

            response = {
                "symbol": result.symbol,
                "current_price": result.current_price,
                "price_change_percentage": result.price_change_percentage,
                "price_range": result.price_range,
                "trend_direction": result.trend_direction,
                "volume_trend": result.volume_trend,
                "support_levels": result.support_levels,
                "resistance_levels": result.resistance_levels,
                "moving_averages": result.moving_averages,
                "analysis_period": period
            }
            logger.info(f"✅ Price analysis successful for {symbol}: ${response['current_price']}")
            return response

        except Exception as e:
            logger.error(f"❌ Price analysis failed for {symbol}: {e}")
            return {
                "symbol": symbol,
                "current_price": 0,
                "price_change_percentage": 0,
                "price_range": "N/A",
                "trend_direction": "unknown",
                "volume_trend": "unknown",
                "support_levels": [],
                "resistance_levels": [],
                "moving_averages": {},
                "analysis_period": period,
                "error": f"Failed to get price data: {str(e)}"
            }

    # Tool version for the agent to use
    @Tool
    async def get_price_analysis(symbol: str, period: str = "1month") -> Dict[str, Any]:
        """Tool version - static method"""
        return await AgentTools._get_price_analysis_impl(symbol, period)

    # Static method for news sentiment implementation
    @staticmethod
    async def _get_news_sentiment_impl(symbol: str, max_results: int = 5) -> Dict[str, Any]:
        """Internal implementation - static method"""
        logger.info(f"🔧 News sentiment implementation: {symbol}, {max_results}")
        try:
            # Create tool factory instance inside the static method
            tool_factory = ToolFactory()
            news_tool = tool_factory.get_news_tool()
            result = await news_tool.get_financial_news(symbol, max_results=max_results)

            response = {
                "symbol": result.symbol,
                "overall_sentiment": result.overall_sentiment,
                "fear_greed_index": result.fear_greed_index,
                "key_themes": result.key_themes,
                "top_headlines": [article.title for article in result.articles],
                "article_sentiments": [article.sentiment for article in result.articles if article.sentiment],
                "risk_factors": [f"Negative news: {article.title}" for article in result.articles if article.sentiment == "negative"]
            }
            logger.info(f"✅ News sentiment successful for {symbol}: {response['overall_sentiment']}")
            return response

        except Exception as e:
            logger.error(f"❌ News sentiment failed for {symbol}: {e}")
            return {
                "symbol": symbol,
                "overall_sentiment": "neutral",
                "fear_greed_index": 50,
                "key_themes": [],
                "top_headlines": [],
                "article_sentiments": [],
                "risk_factors": [f"Data unavailable: {str(e)}"]
            }

    # Tool version for the agent to use
    @Tool
    async def get_news_sentiment(symbol: str, max_results: int = 5) -> Dict[str, Any]:
        """Tool version - static method"""
        return await AgentTools._get_news_sentiment_impl(symbol, max_results)

    # Tool for comprehensive analysis
    @Tool
    async def get_comprehensive_analysis(symbol: str, period: str = "1month") -> Dict[str, Any]:
        """
        Get comprehensive financial analysis combining price data and market sentiment
        """
        logger.info(f"🔧 Tool called: get_comprehensive_analysis({symbol}, {period})")
        try:
            # Call the static implementations directly
            price_data = await AgentTools._get_price_analysis_impl(symbol, period)
            news_data = await AgentTools._get_news_sentiment_impl(symbol)

            # Generate insights
            insights = AgentTools._generate_combined_insights(price_data, news_data)

            response = {
                "symbol": symbol,
                "analysis_period": period,
                "price_analysis": price_data,
                "sentiment_analysis": news_data,
                "key_insights": insights,
                "summary": f"Comprehensive analysis of {symbol} over {period}"
            }
            logger.info(f"✅ Comprehensive analysis successful for {symbol}")
            return response

        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed for {symbol}: {e}")
            return {
                "symbol": symbol,
                "analysis_period": period,
                "price_analysis": {},
                "sentiment_analysis": {},
                "key_insights": [f"Analysis failed: {str(e)}"],
                "error": "Unable to complete comprehensive analysis"
            }

    @staticmethod
    def _generate_combined_insights(price_data: Dict[str, Any], news_data: Dict[str, Any]) -> List[str]:
        """Generate insights by combining price and sentiment data"""
        insights = []

        try:
            # Price-based insights
            current_price = price_data.get("current_price", 0)
            if current_price > 0:
                change_pct = price_data.get("price_change_percentage", 0)
                trend = price_data.get("trend_direction", "unknown")

                if trend == "bullish":
                    insights.append(f"Strong upward momentum with {change_pct}% gain over the period")
                elif trend == "bearish":
                    insights.append(f"Facing downward pressure with {change_pct}% decline")

                if price_data.get("volume_trend") == "increasing":
                    insights.append("Increasing trading volume supports the price trend")

            # Sentiment-based insights
            sentiment = news_data.get("overall_sentiment", "neutral")
            fear_greed = news_data.get("fear_greed_index", 50)

            if sentiment == "positive":
                insights.append("Positive market sentiment aligns with recent news flow")
            elif sentiment == "negative":
                insights.append("Market sentiment shows concerns that may impact performance")

            if fear_greed > 70:
                insights.append("High greed index suggests optimistic market sentiment")
            elif fear_greed < 30:
                insights.append("Low fear index may indicate potential buying opportunity")

            # Add headlines if available
            headlines = news_data.get("top_headlines", [])
            if headlines:
                insights.append(f"Recent news includes {len(headlines)} key developments")

        except Exception as e:
            insights.append("Limited insights available due to data constraints")

        return insights[:5] if insights else ["Analysis completed with available market data"]