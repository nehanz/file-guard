from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from app.core.config import settings

class DatabaseConnection:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect(cls) -> None:
        """
        Initialize database connection.
        """
        logger.info(f"Connecting to MongoDB at {settings.DATABASE_URL}")
        cls.client = AsyncIOMotorClient(settings.DATABASE_URL)
        # Test connection
        await cls.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")

    @classmethod
    async def disconnect(cls) -> None:
        """
        Close database connection.
        """
        if cls.client:
            logger.info("Disconnecting from MongoDB")
            cls.client.close()
            logger.info("Successfully disconnected from MongoDB")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """
        Get database instance.
        """
        return cls.client[settings.DATABASE_NAME]

async def get_database_dependency() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    FastAPI Dependency to get database instance.
    """
    yield DatabaseConnection.get_db()
