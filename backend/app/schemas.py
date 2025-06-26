# app/schemas.py
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.
    """
    user_id: int = Field(..., description="ID of the user initiating the chat")
    message: str = Field(..., description="Chat message text")

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.
    """
    reply: str = Field(..., description="AI-generated chat reply")
