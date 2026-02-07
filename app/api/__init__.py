"""API package for transcript analysis endpoints.

This package contains FastAPI routes, schemas, and dependencies.
"""

from app.api.main import app
from app.api.routes import router

__all__ = ["app", "router"]
