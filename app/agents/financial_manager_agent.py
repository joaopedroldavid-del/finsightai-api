from pydantic_ai import Agent
from typing import Optional
import os
from dotenv import load_dotenv

from app.agents.tools.agent_tool import AgentTools

# Load environment variables
load_dotenv()

class FinancialManagerAgent:
    """
    Financial Manager with tool integration
    """

    def __init__(self):
        self.agent: Optional[Agent] = None
        self.agent_tools = AgentTools()

    async def initialize(self) -> Agent:
        if self.agent is None:
            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")

            self.agent = Agent(
                model='openai:gpt-5',
                system_prompt=self._get_system_prompt(),
                tools=[
                    self.agent_tools.get_price_analysis,
                    self.agent_tools.get_news_sentiment,
                    self.agent_tools.get_comprehensive_analysis
                ]
            )
        return self.agent

    def get_agent_type(self) -> str:
        return "financial_manager"

    def _get_system_prompt(self) -> str:
        return """# Financial Analysis Agent

You are a financial analysis expert with access to real-time data tools.

## TOOLS AVAILABLE:
1. get_price_analysis(symbol, period) - Get price data, trends, technical indicators
2. get_news_sentiment(symbol) - Get market sentiment, news, fear/greed index  
3. get_comprehensive_analysis(symbol, period) - Get complete analysis (recommended)

## MANDATORY WORKFLOW:
1. ALWAYS call a tool first to get real data
2. Use get_comprehensive_analysis() for most requests
3. Extract symbol (AAPL, TSLA, BTC, etc.) and period from user message
4. Present ACTUAL data from tool responses

## CRITICAL RULES:
- NEVER invent or estimate numbers - use only tool data
- NO placeholders like "XXXXX" or "XX%" - use actual values
- If tools fail, explain the issue but don't make up data
- Always specify the symbol and period in your response

## TOOL CALL EXAMPLES:
User: "Analyze Bitcoin"
→ Call: get_comprehensive_analysis("BTC", "1month")

User: "Tesla stock news"
→ Call: get_news_sentiment("TSLA")

User: "Apple performance last 3 months"  
→ Call: get_price_analysis("AAPL", "3months")

## RESPONSE STRUCTURE:
1. State what you're analyzing (symbol + period)
2. Present actual price data from tools
3. Present actual sentiment data from tools  
4. Provide insights based on the real data
5. Note any data limitations if tools fail

Your responses must be data-driven and accurate!"""