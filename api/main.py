"""
Aetherion Web Dashboard – FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routers import auth, tasks, agents, council, websocket, oauth_routes
from api.middleware.rate_limit import RateLimiter

app = FastAPI(
    title="Aetherion API",
    description="Autonomous AI Research Institution – Web Dashboard",
    version="3.3.0",
)

# CORS (for React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (30 requests per minute per IP)
app.add_middleware(RateLimiter, requests_per_minute=30)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(council.router, prefix="/api/council", tags=["Council"])
app.include_router(websocket.router, prefix="/api/ws", tags=["WebSocket"])
app.include_router(oauth_routes.router, prefix="/api/oauth", tags=["OAuth"])

# Serve React static files (after building frontend)
app.mount("/", StaticFiles(directory="api/static", html=True), name="static")
