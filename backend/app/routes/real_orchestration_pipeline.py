from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.real_orchestration_pipeline_service import real_orchestration_pipeline_service


router = APIRouter(prefix="/api/real-orchestration", tags=["real-orchestration"])


class OrchestrationRunRequest(BaseModel):
    goal: str
    project: str | None = None
    repo: str | None = None
    context: str | None = None
    priority: str = "normal"
    sensitive: bool = False
    needs_code: bool = False
    needs_large_context: bool = False
    needs_multimodal: bool = False
    preferred_provider: str | None = None
    execution_mode: str = "safe_queue"
    operator_approved: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return real_orchestration_pipeline_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return real_orchestration_pipeline_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": real_orchestration_pipeline_service.rules()}


@router.get("/policy")
def policy() -> dict[str, Any]:
    return real_orchestration_pipeline_service.policy()


@router.post("/run")
def run(request: OrchestrationRunRequest) -> dict[str, Any]:
    return real_orchestration_pipeline_service.run(
        goal=request.goal,
        project=request.project,
        repo=request.repo,
        context=request.context,
        priority=request.priority,
        sensitive=request.sensitive,
        needs_code=request.needs_code,
        needs_large_context=request.needs_large_context,
        needs_multimodal=request.needs_multimodal,
        preferred_provider=request.preferred_provider,
        execution_mode=request.execution_mode,
        operator_approved=request.operator_approved,
    )


@router.post("/simulate")
def simulate(request: OrchestrationRunRequest) -> dict[str, Any]:
    return real_orchestration_pipeline_service.simulate(
        goal=request.goal,
        project=request.project,
        repo=request.repo,
        context=request.context,
        priority=request.priority,
        sensitive=request.sensitive,
        needs_code=request.needs_code,
        needs_large_context=request.needs_large_context,
        needs_multimodal=request.needs_multimodal,
        preferred_provider=request.preferred_provider,
        execution_mode=request.execution_mode,
        operator_approved=request.operator_approved,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return real_orchestration_pipeline_service.package()
