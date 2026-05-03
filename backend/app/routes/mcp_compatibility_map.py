from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.mcp_compatibility_map_service import mcp_compatibility_map_service


router = APIRouter(prefix="/api/mcp-compatibility", tags=["mcp-compatibility"])


class ValidateToolRequest(BaseModel):
    tool_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    operator_approved: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return mcp_compatibility_map_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return mcp_compatibility_map_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": mcp_compatibility_map_service.rules()}


@router.get("/tools")
def tools(
    category: str | None = Query(default=None),
    risk: str | None = Query(default=None),
    ai_callable: bool | None = Query(default=None),
) -> dict[str, Any]:
    return mcp_compatibility_map_service.tools(category=category, risk=risk, ai_callable=ai_callable)


@router.get("/tools/{tool_id}")
def get_tool(tool_id: str) -> dict[str, Any]:
    return mcp_compatibility_map_service.get_tool(tool_id=tool_id)


@router.get("/manifest")
def manifest(include_internal_notes: bool = Query(default=False)) -> dict[str, Any]:
    return mcp_compatibility_map_service.manifest(include_internal_notes=include_internal_notes)


@router.post("/validate-tool")
def validate_tool(request: ValidateToolRequest) -> dict[str, Any]:
    return mcp_compatibility_map_service.validate_tool_call(
        tool_id=request.tool_id,
        payload=request.payload,
        operator_approved=request.operator_approved,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return mcp_compatibility_map_service.package()
