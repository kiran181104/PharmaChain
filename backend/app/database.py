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
        mongodb_url = settings.MONGODB_URL
        logger.info(f"Connecting to MongoDB at {mongodb_url[:50]}...")  # Log partial URL for privacy
        
        database.client = AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=10000,  # 10 second timeout
            connectTimeoutMS=10000
        )
        database.db = database.client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await database.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB (database: {settings.MONGODB_DB_NAME})")
        
        # Create indexes
        try:
            await create_indexes()
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes (non-fatal): {str(e)}")
        
        # Seed dataset
        try:
            await seed_drug_composition_dataset()
            logger.info("Drug composition dataset check complete")
        except Exception as e:
            logger.error(f"Error seeding dataset (non-fatal): {str(e)}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        logger.error(f"MONGODB_URL env var configured: {bool(settings.MONGODB_URL)}")
        logger.warning("Application will continue without database connection. Call POST /api/drugs/dataset/seed manually to initialize the database.")
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


async def seed_drug_composition_dataset():
    """Seed standard drug composition dataset if it is empty."""
    try:
        if not database.db:
            return

        count = await database.db.drug_composition_dataset.count_documents({})
        if count > 0:
            logger.info("Drug composition dataset is already seeded")
            return

        default_data = [
            {
                "drugName": "Paracetamol 500mg",
                "standardComposition": {
                    "ingredients": [
                        {"name": "Paracetamol", "quantity": "500mg", "percentage": 50},
                        {"name": "Microcrystalline Cellulose", "quantity": "200mg", "percentage": 20},
                        {"name": "Starch", "quantity": "150mg", "percentage": 15},
                        {"name": "Magnesium Stearate", "quantity": "100mg", "percentage": 10},
                        {"name": "Povidone", "quantity": "50mg", "percentage": 5}
                    ]
                }
            },
            {
                "drugName": "Ibuprofen 400mg",
                "standardComposition": {
                    "ingredients": [
                        {"name": "Ibuprofen", "quantity": "400mg", "percentage": 44.4},
                        {"name": "Corn Starch", "quantity": "250mg", "percentage": 27.8},
                        {"name": "Microcrystalline Cellulose", "quantity": "150mg", "percentage": 16.7},
                        {"name": "Colloidal Silicon Dioxide", "quantity": "50mg", "percentage": 5.6},
                        {"name": "Magnesium Stearate", "quantity": "50mg", "percentage": 5.6}
                    ]
                }
            },
            {
                "drugName": "Amoxicillin 250mg",
                "standardComposition": {
                    "ingredients": [
                        {"name": "Amoxicillin Trihydrate", "quantity": "250mg", "percentage": 50},
                        {"name": "Microcrystalline Cellulose", "quantity": "100mg", "percentage": 20},
                        {"name": "Sodium Starch Glycolate", "quantity": "75mg", "percentage": 15},
                        {"name": "Magnesium Stearate", "quantity": "50mg", "percentage": 10},
                        {"name": "Talc", "quantity": "25mg", "percentage": 5}
                    ]
                }
            },
            {
                "drugName": "Aspirin 325mg",
                "standardComposition": {
                    "ingredients": [
                        {"name": "Acetylsalicylic Acid", "quantity": "325mg", "percentage": 54.2},
                        {"name": "Corn Starch", "quantity": "150mg", "percentage": 25},
                        {"name": "Microcrystalline Cellulose", "quantity": "75mg", "percentage": 12.5},
                        {"name": "Hypromellose", "quantity": "30mg", "percentage": 5},
                        {"name": "Magnesium Stearate", "quantity": "20mg", "percentage": 3.3}
                    ]
                }
            },
            {
                "drugName": "Metformin 500mg",
                "standardComposition": {
                    "ingredients": [
                        {"name": "Metformin Hydrochloride", "quantity": "500mg", "percentage": 62.5},
                        {"name": "Povidone", "quantity": "150mg", "percentage": 18.75},
                        {"name": "Microcrystalline Cellulose", "quantity": "100mg", "percentage": 12.5},
                        {"name": "Magnesium Stearate", "quantity": "30mg", "percentage": 3.75},
                        {"name": "Hypromellose", "quantity": "20mg", "percentage": 2.5}
                    ]
                }
            },
            {
                "drugName": "Ciprofloxacin 500mg",
                "standardComposition": {
                    "ingredients": [
                        {"name": "Ciprofloxacin Hydrochloride", "quantity": "500mg", "percentage": 55.6},
                        {"name": "Microcrystalline Cellulose", "quantity": "200mg", "percentage": 22.2},
                        {"name": "Crospovidone", "quantity": "100mg", "percentage": 11.1},
                        {"name": "Magnesium Stearate", "quantity": "50mg", "percentage": 5.6},
                        {"name": "Colloidal Silicon Dioxide", "quantity": "50mg", "percentage": 5.6}
                    ]
                }
            }
        ]

        await database.db.drug_composition_dataset.insert_many(default_data)
        logger.info("Seeded drug composition dataset with default entries")

    except Exception as e:
        logger.error(f"Failed to seed drug composition dataset: {str(e)}")


def get_database():
    """
    Get database instance
    """
    return database.db
