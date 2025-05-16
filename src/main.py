"""Main FastAPI application."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.job_api import router as job_router
from src.core.config import settings
from src.core.logging import setup_logging

app = FastAPI(
    title="JobScraper API",
    description="API for scraping jobs from multiple sources",
    version="1.0.0",
)

# Setup logging
setup_logging()

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    