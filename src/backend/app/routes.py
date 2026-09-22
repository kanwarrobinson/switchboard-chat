from fastapi import APIRouter, HTTPException, status
from app.models import (
    ChatRequest,
    ChatResponse,
    SessionSummary,
    SessionDetail,
    HealthResponse,
    Message
)
from app.database import db
from app.chat_graph import ChatGraph
from app.llm_client import get_llm_client
from app.utils import generate_session_id, detect_query_type, extract_model_from_response
from datetime import datetime
from typing import List
import structlog

logger = structlog.get_logger()

router = APIRouter()

# Global chat graph instance (will be initialized on startup)
chat_graph = None


def init_chat_graph(use_mock_llm: bool = True):
    """Initialize the chat graph with LLM client"""
    global chat_graph

    # Get LLM client (mock for local testing)
    llm_client = get_llm_client(use_mock=use_mock_llm)

    # Create chat graph
    chat_graph = ChatGraph(llm_client)
    chat_graph.setup_checkpointer()
    chat_graph.build_graph()

    logger.info("chat_graph_initialized", mock=use_mock_llm)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message and get AI response.

    Args:
        request: Chat request with message and optional session_id

    Returns:
        Chat response with AI-generated reply
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or generate_session_id()

        # Get conversation history to detect query type
        history = chat_graph.get_conversation_history(session_id)
        query_type = detect_query_type(request.message, history)

        logger.info(
            "chat_request",
            session_id=session_id,
            message_length=len(request.message),
            query_type=query_type,
            history_length=len(history)
        )

        # Invoke chat graph
        ai_message = await chat_graph.ainvoke(
            message=request.message,
            session_id=session_id,
            query_type=query_type
        )

        # Extract model info
        model_used = ai_message.additional_kwargs.get("model", "unknown")
        fallback_triggered = ai_message.additional_kwargs.get("fallback_triggered", False)

        # Determine provider
        provider = "unknown"
        if "gpt" in model_used.lower():
            provider = "openai"
        elif "claude" in model_used.lower():
            provider = "anthropic"
        elif "llama" in model_used.lower() or "mistral" in model_used.lower():
            provider = "self-hosted"

        logger.info(
            "chat_response",
            session_id=session_id,
            model_used=model_used,
            provider=provider,
            query_type=query_type,
            fallback=fallback_triggered
        )

        return ChatResponse(
            session_id=session_id,
            response=ai_message.content,
            model_used=model_used,
            provider=provider,
            query_type=query_type,
            fallback_triggered=fallback_triggered,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error("chat_endpoint_error", error=str(e), session_id=request.session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionSummary])
async def list_sessions():
    """
    List all conversation sessions.

    Returns:
        List of session summaries
    """
    try:
        # Get all sessions from MongoDB conversations collection
        conversations_collection = db.get_database()["conversations"]

        # Get all sessions, sorted by updated_at
        sessions_cursor = conversations_collection.find().sort("updated_at", -1).limit(50)

        sessions = []
        for session_doc in sessions_cursor:
            messages = session_doc.get("messages", [])
            message_count = len(messages)

            # Get last message preview
            last_message_preview = None
            if messages:
                last_msg = messages[-1]
                content = last_msg.get("content", "")
                last_message_preview = content[:100]

            sessions.append(
                SessionSummary(
                    session_id=session_doc["session_id"],
                    created_at=session_doc.get("created_at", datetime.utcnow()),
                    updated_at=session_doc.get("updated_at", datetime.utcnow()),
                    message_count=message_count,
                    last_message_preview=last_message_preview
                )
            )

        return sessions

    except Exception as e:
        logger.error("list_sessions_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    """
    Get detailed session with full message history.

    Args:
        session_id: Session ID

    Returns:
        Session detail with messages
    """
    try:
        # Get conversation from MongoDB
        mongo_db = db.get_database()
        conversations = mongo_db["conversations"]

        session_doc = conversations.find_one({"session_id": session_id})

        if not session_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Convert to Message objects
        messages = []
        for msg_doc in session_doc.get("messages", []):
            metadata = msg_doc.get("metadata", {})

            # Determine provider from model
            model_used = metadata.get("model")
            provider = None
            if model_used:
                if "gpt" in model_used.lower():
                    provider = "openai"
                elif "claude" in model_used.lower():
                    provider = "anthropic"
                elif "llama" in model_used.lower() or "mistral" in model_used.lower():
                    provider = "self-hosted"

            messages.append(
                Message(
                    message_id=generate_session_id(),
                    role=msg_doc["role"],
                    content=msg_doc["content"],
                    timestamp=msg_doc.get("timestamp", datetime.utcnow()),
                    model_used=model_used,
                    provider=provider,
                    query_type=msg_doc.get("query_type"),
                    fallback_triggered=metadata.get("fallback_triggered", False)
                )
            )

        return SessionDetail(
            session_id=session_id,
            messages=messages,
            created_at=session_doc.get("created_at", datetime.utcnow()),
            updated_at=session_doc.get("updated_at", datetime.utcnow()),
            message_count=len(messages)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_session_error", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    # Check MongoDB
    mongodb_status = "connected" if db.health_check() else "disconnected"

    # TODO: Check gateway health when available
    gateway_status = None

    overall_status = "ok" if mongodb_status == "connected" else "degraded"

    return HealthResponse(
        status=overall_status,
        mongodb=mongodb_status,
        gateway=gateway_status,
        timestamp=datetime.utcnow()
    )
