import httpx
from typing import List, Dict, Optional
from datetime import datetime
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class PriceDataRequest( BaseModel ):
    symbol: str = Field( ..., description="Stock or cryptocurrency symbol ( e.g., AAPL, BTC )" )
    period: str = Field( default="1month", description="Analysis period: 1week, 2weeks, 1month, 3months, 6months, 1year" )
    interval: str = Field( default="1d", description="Data interval: 1d, 1h, 1w" )


class PriceAnalysisResult( BaseModel ):
    symbol: str
    current_price: float
    price_change_percentage: float
    price_range: str
    trend_direction: str
    volume_trend: str
    support_levels: List[float]
    resistance_levels: List[float]
    moving_averages: Dict[str, float]
    rsi: Optional[float] = None
    timestamp: datetime


class PriceAnalysisTool:
    """
    Tool for analyzing stock and cryptocurrency prices
    Uses Yahoo Finance API for real data
    """

    def __init__( self ):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    async def get_price_data( self, symbol: str, period: str = "1month", interval: str = "1d" ) -> PriceAnalysisResult:
        """
        Get comprehensive price analysis for a stock or cryptocurrency

        Args:
            symbol: Stock symbol ( AAPL ) or cryptocurrency ( BTC-USD )
            period: Time period for analysis
            interval: Data interval
        """
        try:
            symbol_upper = symbol.upper()
            has_suffix = any( ext in symbol_upper for ext in ['-USD', '.SA', '.AX', '.L', '.TO'] )

            if not has_suffix:
                if symbol_upper in ['BTC','ETH','USDT','BNB','XRP','SOL','USDC','DOGE','ADA','TRX','LINK','LTC','BCH','XLM','SUI','AVAX','HBAR','ZEC','ETC','NEO','XMR','DOGE','FIL','APE','MKR','ATOM','THETA','EOS','ALGO','VET']:
                    formatted_symbol = f"{symbol_upper}-USD"
                else:
                    formatted_symbol = symbol_upper
            else:
                formatted_symbol = symbol_upper

            period_map = {
                "1week": "5d",
                "2weeks": "10d",
                "1month": "1mo",
                "3months": "3mo",
                "6months": "6mo",
                "1year": "1y"
            }

            yahoo_period = period_map.get( period, "1mo" )

            async with httpx.AsyncClient( timeout=30.0 ) as client:
                url = f"{self.base_url}/{formatted_symbol}"
                params = {
                    "range": yahoo_period,
                    "interval": interval,
                    "includePrePost": "false"
                }

                headers = {
                    "User-Agent": "Mozilla/5.0 ( Windows NT 10.0; Win64; x64 ) AppleWebKit/537.36 ( KHTML, like Gecko ) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://finance.yahoo.com/",
                }
                
                response = await client.get( url, params=params, headers=headers )
                response.raise_for_status()
                data = response.json()

                result = data['chart']['result'][0]
                quotes = result['indicators']['quote'][0]
                timestamps = result['timestamp']
                highs = quotes['high']
                lows = quotes['low']
                closes = quotes['close']
                volumes = quotes['volume']

                current_price = closes[-1] if closes else 0
                start_price = closes[0] if closes else current_price
                price_change_pct = ( ( current_price - start_price ) / start_price * 100 ) if start_price else 0

                valid_highs = [h for h in highs if h is not None]
                valid_lows = [l for l in lows if l is not None]
                price_range = f"${min( valid_lows ):.2f}-${max( valid_highs ):.2f}" if valid_highs and valid_lows else "N/A"

                if len( closes ) >= 5:
                    recent_trend = "bullish" if closes[-1] > closes[-5] else "bearish" if closes[-1] < closes[
                        -5] else "neutral"
                else:
                    recent_trend = "neutral"

                if volumes and len(volumes) >= 5:
                    recent_volumes = [v for v in volumes[-5:] if v is not None]

                    if recent_volumes:
                        recent_volume = sum(recent_volumes) / len(recent_volumes)

                        earlier_volumes = [v for v in volumes[-10:-5] if v is not None]
                        earlier_volume = sum(earlier_volumes) / len(
                            earlier_volumes) if earlier_volumes else recent_volume

                        volume_trend = "increasing" if recent_volume > earlier_volume else "decreasing"
                    else:
                        volume_trend = "unknown"
                else:
                    volume_trend = "stable"

                support_levels = self._calculate_support_resistance( lows, "support" )
                resistance_levels = self._calculate_support_resistance( highs, "resistance" )

                moving_averages = self._calculate_moving_averages( closes )

                return PriceAnalysisResult( 
                    symbol=symbol,
                    current_price=current_price,
                    price_change_percentage=round( price_change_pct, 2 ),
                    price_range=price_range,
                    trend_direction=recent_trend,
                    volume_trend=volume_trend,
                    support_levels=support_levels,
                    resistance_levels=resistance_levels,
                    moving_averages=moving_averages,
                    timestamp=datetime.now()
                 )

        except Exception as e:
            logger.error( f"Exception while getting price data: {e} " )

    def _calculate_support_resistance( self, prices: List[float], level_type: str ) -> List[float]:
        """Calculate support/resistance levels"""
        if not prices:
            return []

        valid_prices = [p for p in prices if p is not None]
        if not valid_prices:
            return []

        if level_type == "support":
            significant_levels = [min( valid_prices )]
            if len( valid_prices ) > 10:
                significant_levels.append( sorted( valid_prices )[len( valid_prices ) // 10] )
        else:  # resistance
            significant_levels = [max( valid_prices )]
            if len( valid_prices ) > 10:
                significant_levels.append( sorted( valid_prices )[-len( valid_prices ) // 10] )

        return [round( level, 2 ) for level in significant_levels]

    def _calculate_moving_averages( self, prices: List[float] ) -> Dict[str, float]:
        """Calculate various moving averages"""
        valid_prices = [p for p in prices if p is not None]
        if not valid_prices:
            return {}

        ma_20 = sum( valid_prices[-20:] ) / min( 20, len( valid_prices ) ) if len( valid_prices ) >= 5 else valid_prices[-1]
        ma_50 = sum( valid_prices[-50:] ) / min( 50, len( valid_prices ) ) if len( valid_prices ) >= 10 else ma_20

        return {
            "MA_20": round( ma_20, 2 ),
            "MA_50": round( ma_50, 2 )
        }

    async def _get_mock_price_data( self, symbol: str, period: str ) -> PriceAnalysisResult:
        """Provide mock data when real API fails"""
        mock_prices = {
            "AAPL": {"price": 195.50, "change": 5.2, "range": "185.00-198.00"},
            "TSLA": {"price": 250.75, "change": 8.3, "range": "215.00-235.00"},
            "BTC": {"price": 51250.75, "change": 15.8, "range": "42000.00-52000.00"},
            "ETH": {"price": 2850.25, "change": 12.3, "range": "2400.00-2900.00"},
            "MSFT": {"price": 415.80, "change": 3.7, "range": "400.00-420.00"}
        }

        mock_data = mock_prices.get( symbol.upper(), {"price": 100.0, "change": 2.5, "range": "95.00-105.00"} )

        return PriceAnalysisResult( 
            symbol=symbol,
            current_price=mock_data["price"],
            price_change_percentage=mock_data["change"],
            price_range=mock_data["range"],
            trend_direction="bullish",
            volume_trend="increasing",
            support_levels=[mock_data["price"] * 0.95],
            resistance_levels=[mock_data["price"] * 1.05],
            moving_averages={"MA_20": mock_data["price"], "MA_50": mock_data["price"]},
            timestamp=datetime.now()
         )