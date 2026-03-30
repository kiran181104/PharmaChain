"""
MongoDB Database Connection and Configuration
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, IndexModel
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """
    Database connection manager
    """
    client: AsyncIOMotorClient = None
    db = None


database = Database()


async def connect_to_mongo():
    """
    Connect to MongoDB and create indexes
    """
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000
        )
        database.db = database.client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await database.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        logger.warning("Application will continue without database connection")
        # Don't raise exception - allow app to start without DB
        database.client = None
        database.db = None


async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    try:
        if database.client:
            database.client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")


async def create_indexes():
    """
    Create database indexes for better query performance
    """
    try:
        # Users collection indexes
        users_indexes = [
            IndexModel([("walletAddress", ASCENDING)], unique=True),
            IndexModel([("role", ASCENDING)])
        ]
        await database.db.users.create_indexes(users_indexes)
        
        # Drug composition dataset indexes
        dataset_indexes = [
            IndexModel([("drugName", ASCENDING)], unique=True)
        ]
        await database.db.drug_composition_dataset.create_indexes(dataset_indexes)
        
        # Drug composition storage indexes
        storage_indexes = [
            IndexModel([("batchId", ASCENDING)], unique=True)
        ]
        await database.db.drug_composition_storage.create_indexes(storage_indexes)
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")


def get_database():
    """
    Get database instance
    """
    return database.db
