# pylint: disable=too-few-public-methods

"""Middleware for request timeout handling."""
import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_504_GATEWAY_TIMEOUT

class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware for request timeout handling."""

    def __init__(self, app, timeout_seconds: int = 60):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            if time.time() - start_time > self.timeout_seconds:
                raise HTTPException(
                    status_code=HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out"
                ) from e
            raise
