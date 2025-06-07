from typing import List
from pydantic import BaseModel, Field
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="List of messages in the conversation")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI's response to the chat")
    usage: dict = Field(..., description="Token usage information")

class AIAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": msg.role, "content": msg.content} for msg in request.messages],
                model="llama-3.1-8b-instant",
                temperature=0.7
            )
            
            return ChatResponse(
                response=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")