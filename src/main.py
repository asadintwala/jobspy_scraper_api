"""Main FastAPI application."""
import logging
import time

import uvicorn
from aiohttp import ClientSession, ClientTimeout
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from tenacity import retry, stop_after_attempt, wait_exponential

from src.api.job_api import router as job_router
from src.core.config import settings
from src.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JobScraper API",
    description="API for scraping jobs from multiple sources",
    version="1.0.0",
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all API requests and responses."""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    logger.info(f"Query params: {dict(request.query_params)}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(f"Response: {response.status_code} - Processed in {process_time:.2f}s")

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
