from app.agents.financial_manager_agent import FinancialManagerAgent
from app.models.schemas import AgentType

class AgentFactory:

    @staticmethod
    async def create_financial_manager():
        agent = FinancialManagerAgent()
        return await agent.initialize()

    @staticmethod
    async def create_agent(agent_type: AgentType):
        if agent_type == AgentType.FINANCIAL_MANAGER:
            return await AgentFactory.create_financial_manager()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")