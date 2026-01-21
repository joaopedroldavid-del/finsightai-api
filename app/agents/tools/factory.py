from app.agents.tools.price_tool import PriceAnalysisTool
from app.agents.tools.news_tool import NewsAnalysisTool


class ToolFactory:
    """Factory for creating and managing tools"""

    def __init__(self):
        self._tools = {}

    def get_price_tool(self) -> PriceAnalysisTool:
        """Get price analysis tool"""
        if "price" not in self._tools:
            self._tools["price"] = PriceAnalysisTool()
        return self._tools["price"]

    def get_news_tool(self) -> NewsAnalysisTool:
        """Get news analysis tool"""
        if "news" not in self._tools:
            self._tools["news"] = NewsAnalysisTool()
        return self._tools["news"]

    def get_all_tools(self):
        """Get all available tools"""
        return {
            "price_tool": self.get_price_tool(),
            "news_tool": self.get_news_tool()
        }