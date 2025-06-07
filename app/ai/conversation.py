from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from schemas.models import ChatConversation, ChatMessage
from sqlalchemy.orm import Session

class Conversation(BaseModel):
    id: str = Field(..., description="Unique conversation ID")
    messages: List[Dict] = Field(default_factory=list, description="List of messages in the conversation")
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    context: Dict = Field(default_factory=dict, description="Additional context for the conversation")

class ConversationManager:
    def create_conversation(self, db: Session, conversation_id: Optional[str] = None, user_id: Optional[int] = None) -> ChatConversation:
        conversation = ChatConversation(user_id=user_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_conversation(self, db: Session, conversation_id: int) -> Optional[ChatConversation]:
        return db.query(ChatConversation).filter(ChatConversation.id == conversation_id).first()

    def add_message(self, db: Session, conversation_id: int, role: str, content: str):
        conversation = self.get_conversation(db, conversation_id)
        if not conversation:
            conversation = self.create_conversation(db, conversation_id)
        message = ChatMessage(conversation_id=conversation.id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_context(self, db: Session, conversation_id: int, max_messages: int = 10) -> List[Dict]:
        conversation = self.get_conversation(db, conversation_id)
        if not conversation:
            return []
        messages = db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.timestamp).all()
        recent_messages = messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent_messages]

    def update_context(self, conversation_id: str, context: Dict):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.context.update(context)
            conversation.last_updated = datetime.now() 