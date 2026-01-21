from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class AnalysisPeriod( str, Enum ):
    ONE_WEEK = "1week"
    TWO_WEEKS = "2weeks"
    ONE_MONTH = "1month"
    THREE_MONTHS = "3months"
    SIX_MONTHS = "6months"
    ONE_YEAR = "1year"


class PriceSnapshot( BaseModel ):
    current_price: float = Field( ..., description="Current market price" )
    price_change_percentage: float = Field( ..., description="Percentage change over period" )
    price_range: str = Field( ..., description="Trading range ( high - low )" )
    trend_direction: str = Field( ..., description="bullish/bearish/neutral" )
    volume_trend: Optional[str] = Field( None, description="Volume analysis" )
    support_resistance: Optional[List[float]] = Field( None, description="Key support/resistance levels" )


class MarketSentiment( BaseModel ):
    fear_greed_index: Optional[int] = Field( None, description="Fear & Greed Index 0-100" )
    sentiment_score: str = Field( ..., description="positive/negative/neutral" )
    key_drivers: List[str] = Field( ..., description="Main sentiment drivers" )
    risk_factors: List[str] = Field( ..., description="Identified risk factors" )


class FinancialAnalysisResponse( BaseModel ):
    """
    Structured response from the financial manager agent
    """

    presentation: str = Field( ..., description="Opening presentation to customer" )
    asset_symbol: str = Field( ..., description="Analyzed asset symbol" )
    analysis_period: str = Field( ..., description="Time period analyzed" )

    price_snapshot: PriceSnapshot
    market_sentiment: MarketSentiment

    top_news_headlines: List[str] = Field( ..., description="3-5 most important headlines" )
    key_insights: List[str] = Field( ..., description="3-5 synthesized insights" )

    analysis_timestamp: datetime = Field( default_factory=datetime.now )
    data_sources: List[str] = Field( default_factory=list )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }