from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AgentType( str, Enum ):
    FINANCIAL_MANAGER = "financial_manager"

class ChatRequest( BaseModel ):
    message: str = Field( ..., min_length=1, max_length=4000 )
    agent_type: AgentType = Field( default=AgentType.FINANCIAL_MANAGER )
    conversation_id: Optional[str] = Field( None, description="Existing conversation ID" )
    context: Optional[Dict[str, Any]] = Field( default_factory=dict )

class ChatResponse( BaseModel ):
    response: str
    conversation_id: str
    agent_type: AgentType
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = Field( default_factory=dict )

class ConversationHistory( BaseModel ):
    conversation_id: str
    user_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class AgentStatus( BaseModel ):
    agent_type: AgentType
    is_available: bool
    last_health_check: datetime
    version: str