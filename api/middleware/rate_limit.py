from starlette.responses import JSONResponse
from collections import defaultdict
import time


class RateLimiter:
    def __init__(self, app, requests_per_minute: int = 30):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.window = 60       # seconds
        self.requests = defaultdict(list)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = scope["client"][0]
        now = time.time()
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if now - t < self.window
        ]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            response = JSONResponse(
                {"detail": "Rate limit exceeded. Try again later."},
                status_code=429,
            )
            await response(scope, receive, send)
            return

        self.requests[client_ip].append(now)
        await self.app(scope, receive, send)
