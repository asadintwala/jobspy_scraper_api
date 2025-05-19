"""Main FastAPI application."""
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from aiohttp import ClientSession, ClientTimeout
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from tenacity import retry, stop_after_attempt, wait_exponential

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

class BaseScraper:
    '''Base Scraper class that handles asynchronous HTTP requests with retries'''
    def __init__(self):
        self.timeout = ClientTimeout(total=30) # Set a total timeout of 30 seconds for each HTTP request
        self.session = ClientSession(timeout=self.timeout)

    # Retry the function up to 3 times if it fails & Wait between retries: exponential backoff (ex, 4s, max 10s)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_data(self, url: str):
        '''
        Asynchronously fetch JSON data from the given URL using an HTTP GET request.
        Automatically retries the request on failure based on the retry policy.

        Args:
            url (str): The URL to fetch data from.

        Returns:
            dict: Parsed JSON response from the URL.
        '''
        async with self.session.get(url) as response:
            return await response.json()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
