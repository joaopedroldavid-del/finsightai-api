from fastapi import APIRouter, Depends
from app.services.financial_manager_service import AgentService
from app.core.dependencies import get_agent_service

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "financial-agent-api"}

@router.get("/agents")
async def agents_health_check(
        agent_service: AgentService = Depends(get_agent_service)
):
    statuses = await agent_service.get_agent_status()
    all_healthy = all(status.is_available for status in statuses)

    return {
        "status": "healthy" if all_healthy else "degraded",
        "agents": {status.agent_type.value: status.is_available for status in statuses}
    }