from __future__ import annotations

from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Minimal config; you might load from env or YAML in production
LANGFLOW_BASE_URL = "http://langflow:7860"


class ToolDescription(BaseModel):
    name: str
    description: str
    flow_id: str
    input_schema: Dict[str, Any]


class ToolsListResponse(BaseModel):
    tools: List[ToolDescription]


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    result: Dict[str, Any]


# Hard-coded mapping of tools to Langflow flow IDs (align with flows/*.flow.json)
TOOLS: Dict[str, ToolDescription] = {
    "support_rag.query": ToolDescription(
        name="support_rag.query",
        description="Query the support RAG flow using Langflow.",
        flow_id="support/support_rag.flow.json",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
    ),
    "hr_policy_rag.query": ToolDescription(
        name="hr_policy_rag.query",
        description="Query the HR policy RAG flow using Langflow.",
        flow_id="hr/hr_policy_rag.flow.json",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
    ),
}

app = FastAPI(title="Langflow Tools MCP Server", version="0.1.0")


@app.get("/tools", response_model=ToolsListResponse)
async def tools_list() -> ToolsListResponse:
    return ToolsListResponse(tools=list(TOOLS.values()))


@app.post("/tools/call", response_model=ToolCallResponse)
async def tools_call(payload: ToolCallRequest) -> ToolCallResponse:
    tool = TOOLS.get(payload.tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Unknown tool {payload.tool_name!r}")

    async with httpx.AsyncClient(base_url=LANGFLOW_BASE_URL, timeout=60.0) as client:
        # The exact API depends on your Langflow deployment.
        # Common pattern: POST /api/v1/flows/{flow_id}/run
        resp = await client.post(
            f"/api/v1/flows/{tool.flow_id}/run",
            json={"inputs": payload.arguments},
        )
        resp.raise_for_status()
        data = resp.json()

    return ToolCallResponse(result=data)
