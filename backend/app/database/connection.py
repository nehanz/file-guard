import pymongo
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from app.core.config import settings


class DatabaseConnection:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect(cls) -> None:
        """
        Initialize database connection with a connection pool.
        """
        logger.info(f"Connecting to MongoDB at {settings.DATABASE_URL}")
        cls.client = AsyncIOMotorClient(
            settings.DATABASE_URL,
            maxPoolSize=100,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        await cls.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Initialize Indexes
        await cls._init_indexes()

    @classmethod
    async def _init_indexes(cls) -> None:
        """
        Create necessary database indexes on startup.
        """
        logger.info("Initializing MongoDB indexes...")
        db = cls.get_db()

        # Users Collection
        await db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        await db.users.create_index([("username", pymongo.ASCENDING)], unique=True)
        
        # Files Collection
        await db.files.create_index([("file_hash", pymongo.ASCENDING)])
        await db.files.create_index([("user_id", pymongo.ASCENDING)])
        await db.files.create_index([("blockchain_tx_id", pymongo.ASCENDING)])
        
        # Verification Logs
        await db.verification_logs.create_index([("file_id", pymongo.ASCENDING)])
        await db.verification_logs.create_index([("created_at", pymongo.DESCENDING)])
        
        # Activity Logs
        await db.activity_logs.create_index([("user_id", pymongo.ASCENDING)])
        await db.activity_logs.create_index([("created_at", pymongo.DESCENDING)])
        
        # Refresh Tokens
        await db.refresh_tokens.create_index([("token", pymongo.HASHED)])
        await db.refresh_tokens.create_index([("user_id", pymongo.ASCENDING)])
        await db.refresh_tokens.create_index([("expires_at", pymongo.ASCENDING)], expireAfterSeconds=0)

        logger.info("MongoDB indexes successfully initialized.")

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
