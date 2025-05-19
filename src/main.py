# pylint: disable=broad-exception-caught

"""Main FastAPI application."""
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.job_api import router as job_router
from src.api.log_api import router as log_router
from src.core.config import settings
from src.core.logging import setup_logging
from src.core.mongodb import MongoDB, RequestLogger

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    # Startup
    await MongoDB.connect_to_mongodb()
    yield
    # Shutdown
    await MongoDB.close_mongodb_connection()

app = FastAPI(
    title="JobScraper API",
    description="API for scraping jobs from multiple sources",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all API requests and responses."""
    start_time = time.time()

    # Log request
    logger.info("Request: %s %s", request.method, request.url.path)
    logger.info("Query params: %s", dict(request.query_params))

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time
    process_time_ms = process_time * 1000  # Convert to milliseconds

    # Log response
    logger.info("Response: %s - Processed in %.2fs", response.status_code, process_time)

    # Store request/response logs in MongoDB
    await RequestLogger.log_request(
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        headers=dict(request.headers),
        client_ip=request.client.host if request.client else None,
        response_status=response.status_code,
        response_time_ms=process_time_ms,
        user_agent=request.headers.get("user-agent")
    )

    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(job_router, prefix="/api/v1")
app.include_router(log_router, prefix="/api/v1/logs", tags=["logs"])

@app.get("/health", tags=["health"])
async def health_check():
    """Check the health of the API and database connection."""
    try:
        # Check MongoDB connection
        if MongoDB.db is None:
            return {"status": "error", "message": "MongoDB not connected"}

        # Try to ping the database
        await MongoDB.db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API and database are working correctly"
        }
    except Exception as e:
        logger.exception("Database connection error")
        return {
            "status": "error",
            "message": f"Database connection error: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
