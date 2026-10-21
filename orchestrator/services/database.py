import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    db.client = AsyncIOMotorClient(mongo_uri)
    db.db = db.client.daemon_grid
    logger.info("Successfully connected to MongoDB.")

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
    logger.info("MongoDB connection closed.")
