from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..schemas.support import SupportQuery, SupportReply

router = APIRouter(prefix="/support", tags=["support"])


# Optional import to avoid hard dependency during early development
try:
    from ..crew.registry import get_crew  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    get_crew = None  # type: ignore[assignment]


def get_tenant_id(request: Request) -> str:
    """
    Resolve tenant_id from request. In production this is filled by AuthContextMiddleware.
    """
    user_ctx = getattr(request.state, "user", None)
    tenant_id: Optional[str] = getattr(user_ctx, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tenant context. Ensure X-Tenant-ID header and auth middleware.",
        )
    return tenant_id


@router.post("/query", response_model=SupportReply)
async def support_query(
    payload: SupportQuery,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> SupportReply:
    """
    Main entrypoint for Support Copilot.

    - Resolves tenant from middleware.
    - Delegates to CrewAI support crew via the crew registry.
    - Returns standardized SupportReply.
    """
    if get_crew is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Support crew registry is not implemented yet.",
        )

    # Crew is typically a thin wrapper around CrewAI agents.
    crew = get_crew(use_case="support", tenant_id=tenant_id, db=db)  # type: ignore[call-arg]

    # We assume a coroutine returning a dict compatible with SupportReply.
    result_dict = await crew.run_support_flow(payload=payload)

    # Ensure output is validated & serialized through the Pydantic schema.
    return SupportReply(**result_dict)
