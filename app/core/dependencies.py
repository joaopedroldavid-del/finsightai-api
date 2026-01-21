import logging
from app.services.financial_manager_service import AgentService
from app.agents.factory import AgentFactory
from app.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)

# Dependency instances
agent_factory = AgentFactory()
conversation_repo = ConversationRepository()
agent_service = AgentService(agent_factory, conversation_repo)

async def get_agent_service() -> AgentService:
    return agent_service

async def initialize_agents():
    try:
        await agent_service.initialize_agents()
        logger.info("✅ All agents initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agents: {str(e)}")
        raise

async def shutdown_agents():
    try:
        logger.info("✅ Agents shutdown complete")
    except Exception as e:
        logger.error(f"❌ Error during agent shutdown: {str(e)}")