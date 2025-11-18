from __future__ import annotations

from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

CRM_BASE_URL = "https://crm.example.com/api"


class LookupCustomerRequest(BaseModel):
    customer_id: str


class LookupCustomerResponse(BaseModel):
    id: str
    name: str
    email: str | None = None
    status: str | None = None
    raw: Dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="CRM MCP Server", version="0.1.0")


@app.get("/tools")
async def tools_list() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "crm.lookup_customer",
                "description": "Look up a customer by ID in the CRM.",
                "input_schema": LookupCustomerRequest.model_json_schema(),
            }
        ]
    }


@app.post("/tools/call")
async def tools_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = payload.get("tool_name")
    arguments = payload.get("arguments") or {}

    if tool_name != "crm.lookup_customer":
        raise HTTPException(status_code=404, detail=f"Unknown tool {tool_name!r}")

    req = LookupCustomerRequest(**arguments)
    async with httpx.AsyncClient(base_url=CRM_BASE_URL, timeout=20.0) as client:
        resp = await client.get(f"/customers/{req.customer_id}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Customer not found")
        resp.raise_for_status()
        data = resp.json()

    result = LookupCustomerResponse(
        id=str(data.get("id", req.customer_id)),
        name=data.get("name", ""),
        email=data.get("email"),
        status=data.get("status"),
        raw=data,
    )
    return {"result": result.model_dump()}
