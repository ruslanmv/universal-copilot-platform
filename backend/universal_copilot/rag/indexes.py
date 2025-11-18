from __future__ import annotations


def index_name(tenant_id: str, use_case: str, source: str) -> str:
    """
    Build a consistent, multi-tenant index name.

    Example: 'tenantA__support__kb' or 'tenantB__legal__contracts'.
    """
    return f"{tenant_id}__{use_case}__{source}"
