from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.models.schemas import ConversationHistory

class ConversationRepository:

    def __init__(self):
        self._conversations: Dict[str, ConversationHistory] = {}

    async def create_conversation(self, user_id: str = "anonymous") -> str:
        conversation_id = str(uuid.uuid4())
        now = datetime.now()

        self._conversations[conversation_id] = ConversationHistory(
            conversation_id=conversation_id,
            user_id=user_id,
            messages=[],
            created_at=now,
            updated_at=now
        )

        return conversation_id

    async def get_conversation(self, conversation_id: str) -> ConversationHistory:
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        return conversation

    async def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        conversation = await self.get_conversation(conversation_id)
        return conversation.messages

    async def add_message(
            self,
            conversation_id: str,
            role: str,
            content: str
    ) -> None:
        conversation = await self.get_conversation(conversation_id)

        conversation.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        conversation.updated_at = datetime.now()