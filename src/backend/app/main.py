from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.config import settings
from app.database import db
from app.routes import router, init_chat_graph

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("application_starting", environment=settings.ENVIRONMENT)

    # Connect to MongoDB
    try:
        db.connect()
    except Exception as e:
        logger.error("mongodb_connection_failed_on_startup", error=str(e))
        # Continue anyway - will show as degraded in health check

    # Initialize chat graph (use mock LLM for local dev)
    use_mock = settings.is_dev()
    init_chat_graph(use_mock_llm=use_mock)

    logger.info("application_started")

    yield

    # Shutdown
    logger.info("application_stopping")
    db.disconnect()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title="Switchboard Chat API",
    description="AI-powered customer support chat backend with multi-provider routing",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Switchboard Chat API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/api")
async def api_root():
    """API root endpoint - for legacy compatibility"""
    return {
        "service": "Switchboard Chat API",
        "endpoints": {
            "chat": "POST /api/chat",
            "sessions": "GET /api/sessions",
            "session_detail": "GET /api/sessions/{session_id}",
            "health": "GET /api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_dev(),
        workers=settings.API_WORKERS
    )
