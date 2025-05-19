# pylint: disable=duplicate-code
# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-positional-arguments
# pylint: disable=unused-argument

"""MongoDB database connection and operations."""
import logging
import uuid
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from src.core.config import settings
from src.models.log_models import RequestLog

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB client for database operations."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    collection: Optional[AsyncIOMotorCollection] = None

    @classmethod
    async def connect_to_mongodb(cls):
        """Connect to MongoDB."""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client.get_database(settings.DB_NAME)
            cls.collection = cls.db.get_collection(settings.COLLECTION_NAME)
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error("Could not connect to MongoDB: %s", e)
            raise

    @classmethod
    async def close_mongodb_connection(cls):
        """Close MongoDB connection."""
        if cls.client is not None:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    async def log_request(cls, request_data: RequestLog):
        """Log request data to MongoDB."""
        if cls.collection is None:
            raise RuntimeError("MongoDB connection not initialized")
        try:
            await cls.collection.insert_one(request_data.model_dump())
            logger.info("Successfully logged request %s", request_data.request_id)
        except Exception as e:
            logger.error("Failed to log request to MongoDB: %s", e)
            raise

    @classmethod
    async def get_logs(cls, skip: int = 0, limit: int = 100):
        """Retrieve logs from MongoDB."""
        if cls.collection is None:
            raise RuntimeError("MongoDB connection not initialized")
        try:
            # First check if collection exists
            collections = await cls.db.list_collection_names()
            if settings.COLLECTION_NAME not in collections:
                logger.warning("Collection %s does not exist", settings.COLLECTION_NAME)
                return []

            cursor = cls.collection.find().skip(skip).limit(limit)
            logs = await cursor.to_list(length=limit)
            logger.info("Retrieved %d logs from MongoDB", len(logs))
            return logs
        except Exception as e:
            logger.error("Failed to retrieve logs from MongoDB: %s", e)
            raise


class RequestLogger:
    """Request logger that logs to MongoDB."""

    @staticmethod
    async def log_request(
        method: str,
        path: str,
        query_params: dict,
        headers: dict,
        client_ip: str,
        response_status: int,
        response_time_ms: float,
        user_agent: str = None
    ):
        """Log request and response details to MongoDB."""

        # Create request log entry
        request_log = RequestLog(
            request_id=str(uuid.uuid4()),
            method=method,
            path=path,
            query_params=query_params,
            headers={k: v for k, v in headers.items() if k.lower() != "authorization"},
            client_ip=client_ip,
            response_status=response_status,
            response_time_ms=response_time_ms,
            user_agent=user_agent
        )

        # Log to MongoDB
        await MongoDB.log_request(request_log)
