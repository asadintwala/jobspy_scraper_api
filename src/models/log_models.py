"""Models for request logging."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RequestLog(BaseModel):
    """Model for API request logs stored in MongoDB."""
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of request")
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    client_ip: Optional[str] = Field(None, description="Client IP address")
    response_status: int = Field(..., description="Response status code")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    user_agent: Optional[str] = Field(None, description="User agent string")
