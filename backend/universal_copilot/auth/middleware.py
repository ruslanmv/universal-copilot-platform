from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


@dataclass
class UserContext:
    user_id: Optional[str]
    tenant_id: Optional[str]
    roles: List[str]


class AuthContextMiddleware(BaseHTTPMiddleware):
    """
    Simple multi-tenant auth/context middleware.

    In production you will:
    - Verify JWT / OIDC tokens (Keycloak, Azure AD, Auth0, etc.)
    - Map claims to tenant_id, user_id, roles
    - Enforce basic security and reject unauthenticated requests

    For now this acts as a clean extension point and parses:
    - X-Tenant-ID header
    - Authorization: Bearer <token> (we treat <token> as user_id placeholder)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = request.headers.get("X-Tenant-ID")
        auth_header = request.headers.get("Authorization")

        user_id: Optional[str] = None
        roles: List[str] = []

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
            # TODO: replace this with real JWT decode + verification
            user_id = token or None

        # Attach context to request.state
        request.state.user = UserContext(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=roles,
        )

        response = await call_next(request)
        return response
