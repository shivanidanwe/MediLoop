"""
MediLoop In-Memory Rate Limiter Middleware.
Protects sensitive authentication, upload, and AI endpoints against Brute-Force and DoS attacks.
"""
import time
from collections import defaultdict
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Store IP timestamp hits: client_ip -> list of timestamps
        self.requests = defaultdict(list)
        self.window_seconds = 60

    def _get_rate_limit(self, path: str) -> int:
        if "/auth" in path:
            return settings.RATE_LIMIT_PER_MINUTE_AUTH
        elif "/prescriptions/upload" in path:
            return settings.RATE_LIMIT_PER_MINUTE_UPLOAD
        elif "/ai/chat" in path:
            return settings.RATE_LIMIT_PER_MINUTE_CHAT
        else:
            return settings.RATE_LIMIT_PER_MINUTE_GENERAL

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path
        now = time.time()

        limit = self._get_rate_limit(path)

        # Cleanup timestamps older than 1 minute window
        timestamps = [ts for ts in self.requests[client_ip] if now - ts < self.window_seconds]
        self.requests[client_ip] = timestamps

        if len(timestamps) >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Too many requests. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                },
                headers={"Retry-After": "60"}
            )

        # Log current request timestamp
        self.requests[client_ip].append(now)
        return await call_next(request)
