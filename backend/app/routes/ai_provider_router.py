from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.ai_provider_router_service import ai_provider_router_service


router = APIRouter(prefix="/api/ai-provider-router", tags=["ai-provider-router"])


class RouteProviderRequest(BaseModel):
    goal: str
    task_tags: list[str] = Field(default_factory=list)
    context: str | None = None
    sensitive: bool = False
    needs_code: bool = False
    needs_large_context: bool = False
    needs_multimodal: bool = False
    primary_failed: bool = False
    provider_availability: dict[str, bool] = Field(default_factory=dict)
    preferred_provider: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return ai_provider_router_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return ai_provider_router_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": ai_provider_router_service.rules()}


@router.get("/providers")
def providers() -> dict[str, Any]:
    return ai_provider_router_service.providers()


@router.get("/policy")
def policy() -> dict[str, Any]:
    return ai_provider_router_service.policy()


@router.post("/route")
def route(request: RouteProviderRequest) -> dict[str, Any]:
    return ai_provider_router_service.route(
        goal=request.goal,
        task_tags=request.task_tags,
        context=request.context,
        sensitive=request.sensitive,
        needs_code=request.needs_code,
        needs_large_context=request.needs_large_context,
        needs_multimodal=request.needs_multimodal,
        primary_failed=request.primary_failed,
        provider_availability=request.provider_availability,
        preferred_provider=request.preferred_provider,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return ai_provider_router_service.package()
