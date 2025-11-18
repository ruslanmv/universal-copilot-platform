from __future__ import annotations

from typing import Any, Callable, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from .support_crew import SupportCrew
from .base_crew import DomainCrew


CrewBuilder = Callable[[str, AsyncSession], DomainCrew]

CREW_BUILDERS: Dict[str, CrewBuilder] = {
    "support": lambda tenant_id, db: SupportCrew(tenant_id=tenant_id, db=db),
    # "hr": lambda tenant_id, db: HRCrew(tenant_id=tenant_id, db=db),
    # "legal": lambda tenant_id, db: LegalCrew(tenant_id=tenant_id, db=db),
}


def get_crew(
    use_case: str,
    tenant_id: str,
    db: AsyncSession,
) -> DomainCrew:
    """
    Resolve and instantiate the crew for a given use case and tenant.

    Later you can:
      - Read use_cases/*.yaml
      - Check TenantUseCaseConfig
      - Implement A/B versions of crews, etc.
    """
    try:
        builder = CREW_BUILDERS[use_case]
    except KeyError as exc:
        raise ValueError(f"No crew builder registered for use_case={use_case!r}") from exc

    return builder(tenant_id, db)
