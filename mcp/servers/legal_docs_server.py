from __future__ import annotations

from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

LEGAL_DOCS_BASE_URL = "https://legal-docs.example.com/api"


class LegalDocSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=10, ge=1, le=100)


class LegalDocHit(BaseModel):
    id: str
    title: str
    url: str
    snippet: str


class LegalDocSearchResponse(BaseModel):
    hits: List[LegalDocHit] = Field(default_factory=list)


app = FastAPI(title="Legal Docs MCP Server", version="0.1.0")


@app.get("/tools")
async def tools_list() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "legal_docs.search",
                "description": "Search internal legal document repository.",
                "input_schema": LegalDocSearchRequest.model_json_schema(),
            }
        ]
    }


@app.post("/tools/call")
async def tools_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = payload.get("tool_name")
    arguments = payload.get("arguments") or {}

    if tool_name != "legal_docs.search":
        raise HTTPException(status_code=404, detail=f"Unknown tool {tool_name!r}")

    req = LegalDocSearchRequest(**arguments)

    async with httpx.AsyncClient(base_url=LEGAL_DOCS_BASE_URL, timeout=20.0) as client:
        resp = await client.get("/search", params={"q": req.query, "limit": req.top_k})
        resp.raise_for_status()
        data = resp.json()

    hits: List[LegalDocHit] = []
    for item in data.get("results", []):
        hits.append(
            LegalDocHit(
                id=str(item.get("id", "")),
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
            )
        )

    return {"result": LegalDocSearchResponse(hits=hits).model_dump()}
