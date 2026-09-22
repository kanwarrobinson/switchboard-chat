from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
import structlog

logger = structlog.get_logger()


class Database:
    """MongoDB connection manager"""

    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[settings.MONGODB_DATABASE]
            logger.info(
                "mongodb_connected",
                host=settings.MONGODB_HOST,
                database=settings.MONGODB_DATABASE
            )
        except ConnectionFailure as e:
            logger.error("mongodb_connection_failed", error=str(e))
            raise

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("mongodb_disconnected")

    def get_database(self):
        """Get database instance"""
        return self.db

    def health_check(self) -> bool:
        """Check if MongoDB is accessible"""
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
        except Exception as e:
            logger.error("mongodb_health_check_failed", error=str(e))
        return False


# Global database instance
db = Database()
