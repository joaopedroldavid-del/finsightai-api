from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.models.schemas import ChatRequest, ChatResponse, ConversationHistory, AgentStatus
from app.services.financial_manager_service import AgentService
from app.core.dependencies import get_agent_service
from app.core.exceptions import AgentException

logger = logging.getLogger( __name__ )

router = APIRouter( prefix="/api/v1/agents", tags=["agents"] )

@router.post( "/chat", response_model=ChatResponse )
async def chat_with_agent( 
        request: ChatRequest,
        agent_service: AgentService = Depends( get_agent_service )
 ) -> ChatResponse:
    try:
        logger.info( f"Processing chat request for agent: {request.agent_type}" )

        response = await agent_service.process_message( 
            message=request.message,
            agent_type=request.agent_type,
            conversation_id=request.conversation_id,
            context=request.context or {}
         )

        return response

    except AgentException as e:
        raise e
    except Exception as e:
        logger.error( f"Unexpected error processing chat request: {str( e )}" )
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
         )


@router.get( "/conversations/{conversation_id}", response_model=ConversationHistory )
async def get_conversation_history( 
        conversation_id: str,
        agent_service: AgentService = Depends( get_agent_service )
 ) -> ConversationHistory:
    return await agent_service.get_conversation_history( conversation_id )


@router.get( "/status", response_model=List[AgentStatus] )
async def get_agent_status( 
        agent_service: AgentService = Depends( get_agent_service )
 ) -> List[AgentStatus]:
    return await agent_service.get_agent_status()


@router.post( "/conversations", response_model=dict )
async def create_conversation( 
        agent_service: AgentService = Depends( get_agent_service )
 ) -> dict:
    conversation_id = await agent_service.conversation_repo.create_conversation()
    return {"conversation_id": conversation_id, "message": "Conversation created successfully"}