from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    session_id: str = Field(..., description="Session ID (generated if not provided)")
    response: str = Field(..., description="AI assistant response")
    model_used: Optional[str] = Field(None, description="Model that generated the response")
    provider: Optional[str] = Field(None, description="Provider (openai, anthropic, self-hosted)")
    query_type: Optional[str] = Field(None, description="Query type (faq or escalation)")
    fallback_triggered: bool = Field(False, description="Whether failover was triggered")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    """Message model"""
    message_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    query_type: Optional[str] = None
    model_used: Optional[str] = None
    provider: Optional[str] = None
    fallback_triggered: bool = False


class SessionSummary(BaseModel):
    """Summary of a conversation session"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: Optional[str] = None


class SessionDetail(BaseModel):
    """Detailed session with full message history"""
    session_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    message_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    mongodb: str
    gateway: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
