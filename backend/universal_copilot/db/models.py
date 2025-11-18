from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Tenant(Base):
    __tablename__ = "tenants"

    # Override id to use string UUID
    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_uuid, unique=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    default_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    enabled_use_cases: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    use_case_configs: Mapped[List["TenantUseCaseConfig"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    provider_configs: Mapped[List["ProviderConfig"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class UseCase(Base):
    __tablename__ = "use_cases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant_configs: Mapped[List["TenantUseCaseConfig"]] = relationship(
        back_populates="use_case", cascade="all, delete-orphan"
    )


class TenantUseCaseConfig(Base):
    __tablename__ = "tenant_use_case_configs"

    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    use_case_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("use_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )

    crew_name: Mapped[str] = mapped_column(String(255), nullable=False)
    flow_ids: Mapped[Dict[str, str]] = mapped_column(
        JSON, default=dict
    )  # e.g. {"rag": "support/support_rag.flow.json"}
    llm_policy: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict
    )  # e.g. {"provider": "openai", "model": "gpt-4.1-mini", "max_tokens": 2048}

    tenant: Mapped[Tenant] = relationship(back_populates="use_case_configs")
    use_case: Mapped[UseCase] = relationship(back_populates="tenant_configs")


class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False)
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict
    )  # non-secret config (region, endpoint, etc.)

    tenant: Mapped[Tenant] = relationship(back_populates="provider_configs")


class LLMCallLog(Base):
    __tablename__ = "llm_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    tenant_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    use_case_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    provider_name: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)

    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(32), default="success")  # success / error
    error_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    request_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)


class ToolCallLog(Base):
    __tablename__ = "tool_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    tenant_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    use_case_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    mcp_virtual_server: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="success")

    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DocumentSource(Base):
    __tablename__ = "document_sources"

    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    use_case_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    source_type: Mapped[str] = mapped_column(String(64), nullable=False)  # sharepoint, s3, etc.
    uri: Mapped[str] = mapped_column(String(512), nullable=False)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)


class VectorIndex(Base):
    __tablename__ = "vector_indexes"

    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    use_case_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    engine: Mapped[str] = mapped_column(String(64), nullable=False)  # milvus, qdrant, pgvector, etc.
    index_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
