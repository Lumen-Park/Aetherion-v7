"""
Aetherion API Package
Exports FastAPI app and routers.
"""

from api.main import app
from api.routers import auth, tasks, agents, council, websocket, oauth_routes

__all__ = [
    "app",
    "auth",
    "tasks",
    "agents",
    "council",
    "websocket",
    "oauth_routes",
]
