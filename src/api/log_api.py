"""API endpoints for log management."""
from typing import List, Dict, Any
from fastapi import APIRouter, Query

from src.core.mongodb import MongoDB

router = APIRouter()

@router.get("/logs", response_model=List[Dict[str, Any]])
async def get_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    """
    Retrieve API request logs.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of log entries
    """
    return await MongoDB.get_logs(skip=skip, limit=limit)
