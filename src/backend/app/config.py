import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration"""

    # MongoDB
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT: int = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "switchboard_chat")
    MONGODB_USERNAME: str = os.getenv("MONGODB_USERNAME", "root")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "rootpassword")

    @property
    def MONGODB_URI(self) -> str:
        # If no username/password, connect without auth (local development)
        if not self.MONGODB_USERNAME or not self.MONGODB_PASSWORD:
            return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}"
        return f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/?authSource=admin"

    # AI Gateway
    GATEWAY_BASE_URL: str = os.getenv("GATEWAY_BASE_URL", "http://localhost:8080/v1")
    GATEWAY_TIMEOUT: int = int(os.getenv("GATEWAY_TIMEOUT", "30"))

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "1"))

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost"
    ).split(",")

    # LangGraph
    LANGGRAPH_CHECKPOINT_COLLECTION: str = "checkpoints"

    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "development"


settings = Settings()
