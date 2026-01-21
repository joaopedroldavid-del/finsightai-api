import os

import httpx
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class NewsRequest(BaseModel):
    symbol: str = Field(..., description="Stock or cryptocurrency symbol to search news for")
    query: Optional[str] = Field(None, description="Specific search query")
    max_results: int = Field(default=5, description="Maximum number of news articles to return")


class NewsArticle(BaseModel):
    title: str
    source: str
    published_at: str
    description: Optional[str] = None
    url: Optional[str] = None
    sentiment: Optional[str] = None


class NewsAnalysisResult(BaseModel):
    symbol: str
    articles: List[NewsArticle]
    overall_sentiment: str
    fear_greed_index: Optional[int] = None
    key_themes: List[str]
    timestamp: datetime


class NewsAnalysisTool:
    """
    Tool for analyzing financial news and market sentiment
    Uses NewsAPI for real news data (fallback to mock data)
    """

    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"

    async def get_financial_news(self, symbol: str, query: Optional[str] = None,
                                 max_results: int = 5) -> NewsAnalysisResult:
        """
        Get recent financial news and sentiment analysis for a symbol

        Args:
            symbol: Stock or cryptocurrency symbol
            query: Optional specific search query
            max_results: Number of articles to return
        """
        try:
            if self.news_api_key:
                return await self._get_real_news(symbol, query, max_results)
            else:
                return await self._get_mock_news(symbol, query, max_results)

        except Exception as e:
            return await self._get_mock_news(symbol, query, max_results)

    async def _get_real_news(self, symbol: str, query: Optional[str], max_results: int) -> NewsAnalysisResult:
        """Get real news data from NewsAPI"""
        search_query = query or f"{symbol} stock OR {symbol} shares OR {symbol} earnings"

        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "q": search_query,
                "apiKey": self.news_api_key,
                "pageSize": max_results,
                "sortBy": "publishedAt",
                "language": "en",
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            }

            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article_data in data.get('articles', [])[:max_results]:
                article = NewsArticle(
                    title=article_data.get('title', ''),
                    source=article_data.get('source', {}).get('name', 'Unknown'),
                    published_at=article_data.get('publishedAt', ''),
                    description=article_data.get('description'),
                    url=article_data.get('url')
                )
                article.sentiment = self._analyze_sentiment(article.title + " " + (article.description or ""))
                articles.append(article)

            overall_sentiment = self._calculate_overall_sentiment(articles)
            fear_greed_index = self._calculate_fear_greed_index(articles)
            key_themes = self._extract_key_themes(articles)

            return NewsAnalysisResult(
                symbol=symbol,
                articles=articles,
                overall_sentiment=overall_sentiment,
                fear_greed_index=fear_greed_index,
                key_themes=key_themes,
                timestamp=datetime.now()
            )

    async def _get_mock_news(self, symbol: str, query: Optional[str], max_results: int) -> NewsAnalysisResult:
        """Provide mock news data when real API is unavailable"""
        mock_news = {
            "AAPL": [
                {"title": "Apple announces record iPhone sales", "source": "Bloomberg", "sentiment": "positive"},
                {"title": "New Apple AI features impress analysts", "source": "CNBC", "sentiment": "positive"},
                {"title": "Apple faces regulatory challenges in EU", "source": "Reuters", "sentiment": "negative"}
            ],
            "TSLA": [
                {"title": "Tesla deliveries exceed expectations", "source": "Wall Street Journal",
                 "sentiment": "positive"},
                {"title": "New Tesla factory accelerates production", "source": "Bloomberg", "sentiment": "positive"},
                {"title": "Tesla faces competition from legacy automakers", "source": "Reuters",
                 "sentiment": "negative"}
            ],
            "BTC": [
                {"title": "Bitcoin ETF approvals drive institutional adoption", "source": "CoinDesk",
                 "sentiment": "positive"},
                {"title": "Regulatory clarity improves for cryptocurrencies", "source": "Bloomberg",
                 "sentiment": "positive"},
                {"title": "Market volatility concerns persist", "source": "Reuters", "sentiment": "negative"}
            ]
        }

        symbol_news = mock_news.get(symbol.upper(), [
            {"title": "Strong quarterly earnings reported", "source": "Financial Times", "sentiment": "positive"},
            {"title": "Market shows positive momentum", "source": "Bloomberg", "sentiment": "positive"},
            {"title": "Economic uncertainty affects performance", "source": "Reuters", "sentiment": "negative"}
        ])

        articles = []
        for i, news_item in enumerate(symbol_news[:max_results]):
            articles.append(NewsArticle(
                title=news_item["title"],
                source=news_item["source"],
                published_at=(datetime.now() - timedelta(days=i)).isoformat(),
                sentiment=news_item["sentiment"]
            ))

        overall_sentiment = self._calculate_overall_sentiment(articles)
        fear_greed_index = self._calculate_fear_greed_index(articles)
        key_themes = self._extract_key_themes(articles)

        return NewsAnalysisResult(
            symbol=symbol,
            articles=articles,
            overall_sentiment=overall_sentiment,
            fear_greed_index=fear_greed_index,
            key_themes=key_themes,
            timestamp=datetime.now()
        )

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        text_lower = text.lower()
        positive_words = ['bullish', 'positive', 'strong', 'record', 'beat', 'growth', 'profit', 'gain', 'rise', 'up']
        negative_words = ['bearish', 'negative', 'weak', 'loss', 'fall', 'drop', 'decline', 'risk', 'concern', 'down']

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _calculate_overall_sentiment(self, articles: List[NewsArticle]) -> str:
        """Calculate overall sentiment from articles"""
        if not articles:
            return "neutral"

        sentiments = [article.sentiment for article in articles if article.sentiment]
        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _calculate_fear_greed_index(self, articles: List[NewsArticle]) -> int:
        """Calculate a simple fear & greed index"""
        if not articles:
            return 50

        sentiments = [article.sentiment for article in articles if article.sentiment]
        positive_count = sentiments.count("positive")
        total = len(sentiments)

        if total == 0:
            return 50

        # Scale 0-100 based on positive sentiment ratio
        base_score = (positive_count / total) * 100

        # Adjust based on recent trends (mock adjustment)
        adjustments = {
            "positive": +10,
            "negative": -10,
            "neutral": 0
        }

        overall_sentiment = self._calculate_overall_sentiment(articles)
        adjusted_score = base_score + adjustments.get(overall_sentiment, 0)

        return max(0, min(100, int(adjusted_score)))

    def _extract_key_themes(self, articles: List[NewsArticle]) -> List[str]:
        """Extract key themes from news articles"""
        themes = []
        for article in articles:
            title_lower = article.title.lower()
            if any(word in title_lower for word in ['earnings', 'profit', 'revenue']):
                themes.append("Financial Performance")
            if any(word in title_lower for word in ['product', 'launch', 'release']):
                themes.append("Product Development")
            if any(word in title_lower for word in ['regulation', 'legal', 'law']):
                themes.append("Regulatory Environment")
            if any(word in title_lower for word in ['partnership', 'deal', 'acquisition']):
                themes.append("Business Partnerships")
            if any(word in title_lower for word in ['market', 'trading', 'volume']):
                themes.append("Market Activity")

        # Return unique themes
        return list(set(themes))[:5]