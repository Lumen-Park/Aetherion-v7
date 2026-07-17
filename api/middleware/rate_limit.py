from starlette.responses import JSONResponse
import time
import os


class RateLimiter:
    """
    Redis-backed distributed rate limiter.
    Works correctly across multiple Uvicorn workers.
    Falls back to in-memory if Redis is unavailable.
    """

    def __init__(self, app, requests_per_minute: int = 30):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.window = 60  # seconds
        self._redis = None
        self._in_memory_fallback = {}
        self._init_redis()

    def _init_redis(self):
        try:
            import redis
            redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
            self._redis = redis.from_url(redis_url, socket_connect_timeout=1)
            self._redis.ping()
        except Exception:
            self._redis = None

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = scope["client"][0] if scope.get("client") else "unknown"
        now = time.time()
        key = f"rate_limit:{client_ip}"

        if self._redis:
            try:
                self._redis.zremrangebyscore(key, 0, now - self.window)
                count = self._redis.zcard(key)
                if count >= self.requests_per_minute:
                    response = JSONResponse(
                        {"detail": "Rate limit exceeded. Try again later."},
                        status_code=429,
                    )
                    await response(scope, receive, send)
                    return
                self._redis.zadd(key, {f"{now}:{os.urandom(8).hex()}": now})
                self._redis.expire(key, self.window)
            except Exception:
                self._handle_in_memory_fallback(client_ip, now)
        else:
            self._handle_in_memory_fallback(client_ip, now)

        await self.app(scope, receive, send)

    def _handle_in_memory_fallback(self, client_ip, now):
        """In-memory fallback — per-worker only."""
        if client_ip not in self._in_memory_fallback:
            self._in_memory_fallback[client_ip] = []
        self._in_memory_fallback[client_ip] = [
            t for t in self._in_memory_fallback[client_ip] if now - t < self.window
        ]
        if len(self._in_memory_fallback[client_ip]) >= self.requests_per_minute:
            raise Exception("rate_limited")
        self._in_memory_fallback[client_ip].append(now)
