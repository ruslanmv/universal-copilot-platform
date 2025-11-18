from __future__ import annotations

from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

HRIS_BASE_URL = "https://hris.example.com/api"


class GetEmployeeBenefitsRequest(BaseModel):
    employee_id: str


class GetEmployeeBenefitsResponse(BaseModel):
    employee_id: str
    plans: list[Dict[str, Any]] = Field(default_factory=list)


app = FastAPI(title="HRIS MCP Server", version="0.1.0")


@app.get("/tools")
async def tools_list() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "hr.get_employee_benefits",
                "description": "Fetch benefits information for an employee from HRIS.",
                "input_schema": GetEmployeeBenefitsRequest.model_json_schema(),
            }
        ]
    }


@app.post("/tools/call")
async def tools_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = payload.get("tool_name")
    arguments = payload.get("arguments") or {}

    if tool_name != "hr.get_employee_benefits":
        raise HTTPException(status_code=404, detail=f"Unknown tool {tool_name!r}")

    req = GetEmployeeBenefitsRequest(**arguments)

    async with httpx.AsyncClient(base_url=HRIS_BASE_URL, timeout=20.0) as client:
        resp = await client.get(f"/employees/{req.employee_id}/benefits")
        resp.raise_for_status()
        data = resp.json()

    result = GetEmployeeBenefitsResponse(
        employee_id=req.employee_id,
        plans=data.get("plans", []),
    )
    return {"result": result.model_dump()}
