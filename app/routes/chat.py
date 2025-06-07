from fastapi import APIRouter, HTTPException, Header, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from ai.agent import AIAgent, ChatRequest, ChatResponse
from ai.conversation import ConversationManager
import uuid
from auth_utils import verify_access_token

router = APIRouter()
agent = AIAgent()
conversation_manager = ConversationManager()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    conversation_id: Optional[str] = Header(None, alias="X-Conversation-ID"),
    user=Depends(get_current_user)
):
    try:
        # Generate new conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Add user message to conversation history
        for message in request.messages:
            conversation_manager.add_message(conversation_id, message.role, message.content)
        
        # Get conversation context
        context_messages = conversation_manager.get_context(conversation_id)
        
        # Create new request with context
        context_request = ChatRequest(messages=context_messages)
        
        # Get AI response
        response = await agent.chat(context_request)
        
        # Add AI response to conversation history
        conversation_manager.add_message(conversation_id, "assistant", response.response)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str, user=Depends(get_current_user)):
    conversation = conversation_manager.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation 