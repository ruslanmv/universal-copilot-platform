from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..crew.registry import get_crew
from ..schemas.support import SupportQuery, SupportReply
from ..schemas.legal import ContractReviewRequest, ContractReviewResponse


router = APIRouter(prefix="/mcp", tags=["mcp-server"])


class ToolDescription(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


class ToolsListResponse(BaseModel):
    tools: List[ToolDescription]


class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="Fully qualified tool name, e.g. support.answer_ticket.")
    arguments: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = Field(..., description="Tenant identifier.")
    trace_id: str | None = Field(default=None)


class ToolCallResponse(BaseModel):
    result: Dict[str, Any]


@router.get("/tools", response_model=ToolsListResponse)
async def tools_list() -> ToolsListResponse:
    """
    Expose tools to external MCP hosts.

    In a full MCP implementation you would map this onto MCP's tools/list schema.
    """
    tools = [
        ToolDescription(
            name="support.answer_ticket",
            description="Answer a customer support message using support knowledge base.",
            input_schema=SupportQuery.model_json_schema(),
        ),
        ToolDescription(
            name="legal.review_contract",
            description="Review a contract and provide a risk analysis.",
            input_schema=ContractReviewRequest.model_json_schema(),
        ),
    ]
    return ToolsListResponse(tools=tools)


@router.post("/tools/call", response_model=ToolCallResponse)
async def tools_call(payload: ToolCallRequest, db: AsyncSession = Depends(get_db)) -> ToolCallResponse:
    """
    Call a specific tool. This provides a simple HTTP/JSON interface that
    can be wrapped into a full MCP JSON-RPC/stdio server if needed.
    """
    tenant_id = payload.tenant_id
    tool_name = payload.tool_name

    if tool_name == "support.answer_ticket":
        crew = get_crew("support", tenant_id=tenant_id, db=db)
        support_query = SupportQuery(**payload.arguments)
        result_dict = await crew.run_support_flow(support_query)
        reply = SupportReply(**result_dict)
        return ToolCallResponse(result=reply.model_dump())

    if tool_name == "legal.review_contract":
        crew = get_crew("legal", tenant_id=tenant_id, db=db)  # type: ignore[arg-type]
        review_req = ContractReviewRequest(**payload.arguments)
        # you’ll implement .run_contract_review in LegalCrew
        result_dict = await crew.run_contract_review(review_req)  # type: ignore[attr-defined]
        reply = ContractReviewResponse(**result_dict)
        return ToolCallResponse(result=reply.model_dump())

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Unknown tool {tool_name!r}",
    )
