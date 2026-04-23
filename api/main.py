"""
Aetherion Web Dashboard – FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routers import (
    auth,
    tasks,
    agents,
    council,
    websocket,
    oauth_routes,
    constitution,
    agent_catalog,
)
from api.middleware.rate_limit import RateLimiter
from api.metrics import router as metrics_router

app = FastAPI(
    title="Aetherion API",
    description="Autonomous AI Research Institution – Web Dashboard",
    version="3.4.0",
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
app.include_router(constitution.router, prefix="/api", tags=["Constitution"])
app.include_router(agent_catalog.router, prefix="/api", tags=["Agent Catalog"])
app.include_router(metrics_router, prefix="/api", tags=["Metrics"])

# Serve React static files (after building frontend)
app.mount("/", StaticFiles(directory="api/static", html=True), name="static")
