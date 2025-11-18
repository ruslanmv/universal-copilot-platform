from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx

LANGFLOW_BASE_URL = "http://localhost:7860"
FLOWS_DIR = Path("flows")


async def import_flow(client: httpx.AsyncClient, flow_path: Path) -> None:
    with flow_path.open("r", encoding="utf-8") as f:
        flow_json = json.load(f)

    resp = await client.post(
        f"{LANGFLOW_BASE_URL}/api/v1/flows/import",
        json=flow_json,
    )
    resp.raise_for_status()
    print(f"[OK] Imported flow {flow_path}")


async def main() -> None:
    async with httpx.AsyncClient(timeout=60.0) as client:
        for path in FLOWS_DIR.rglob("*.flow.json"):
            await import_flow(client, path)


if __name__ == "__main__":
    asyncio.run(main())
