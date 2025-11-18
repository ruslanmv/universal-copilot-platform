from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.universal_copilot.settings import get_settings
from backend.universal_copilot.db.models import Base, Tenant, UseCase, TenantUseCaseConfig


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database.url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        tenant = Tenant(
            id="tenant_a",
            name="Example Tenant A",
            default_provider="openai",
            enabled_use_cases=["support", "hr", "legal"],
        )
        session.add(tenant)

        for uc_id, name in [
            ("support", "Support Copilot"),
            ("hr", "HR & Learning Copilot"),
            ("legal", "Legal & Risk Copilot"),
        ]:
            uc = UseCase(id=uc_id, name=name, description=name)
            session.add(uc)
            tuc = TenantUseCaseConfig(
                tenant_id="tenant_a",
                use_case_id=uc_id,
                crew_name=f"{uc_id}_crew_v1",
                flow_ids={},
                llm_policy={"provider": "openai", "model": "gpt-4.1-mini"},
            )
            session.add(tuc)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
