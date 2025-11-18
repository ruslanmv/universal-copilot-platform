from __future__ import annotations

from fastapi import APIRouter

from . import routes_health
from . import routes_support

api_router = APIRouter(prefix="/api/v1")


# Core / infra routes
api_router.include_router(routes_health.router)

# Domain routes (only Support for now as example)
api_router.include_router(routes_support.router)

# Later you’ll add:
# from . import routes_hr, routes_legal, ...
# api_router.include_router(routes_hr.router)
# api_router.include_router(routes_legal.router)
api_router.include_router(mcp_server.router)
