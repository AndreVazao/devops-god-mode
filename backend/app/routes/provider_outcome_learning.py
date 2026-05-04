from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.provider_outcome_learning_service import provider_outcome_learning_service

router = APIRouter(prefix="/api/provider-outcome-learning", tags=["provider-outcome-learning"])


class RecordOutcomeRequest(BaseModel):
    provider_id: str
    task_tags: List[str] = Field(default_factory=lambda: ["default"])
    outcome: str
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    latency_ms: Optional[int] = Field(default=None, ge=0)
    cost_hint: str = "unknown"
    failure_reason: str = ""
    sensitive: bool = False
    requires_safety_guard: bool = True
    operator_rating: Optional[int] = Field(default=None, ge=1, le=5)
    notes: str = ""
    project_name: str = "GOD_MODE"


class ScorecardRequest(BaseModel):
    provider_id: Optional[str] = None
    task_tag: Optional[str] = None


class RouterHintsRequest(BaseModel):
    task_tags: List[str] = Field(default_factory=lambda: ["default"])
    sensitive: bool = False


class SimulateRouteRequest(BaseModel):
    goal: str
    task_tags: List[str] = Field(default_factory=list)
    sensitive: bool = False
    needs_code: bool = False
    needs_large_context: bool = False
    needs_multimodal: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return provider_outcome_learning_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return provider_outcome_learning_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return provider_outcome_learning_service.policy()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": provider_outcome_learning_service.rules()}


@router.post("/record-outcome")
def record_outcome(request: RecordOutcomeRequest) -> dict[str, Any]:
    return provider_outcome_learning_service.record_outcome(
        provider_id=request.provider_id,
        task_tags=request.task_tags,
        outcome=request.outcome,
        quality_score=request.quality_score,
        latency_ms=request.latency_ms,
        cost_hint=request.cost_hint,
        failure_reason=request.failure_reason,
        sensitive=request.sensitive,
        requires_safety_guard=request.requires_safety_guard,
        operator_rating=request.operator_rating,
        notes=request.notes,
        project_name=request.project_name,
    )


@router.post("/scorecard")
def scorecard(request: ScorecardRequest) -> dict[str, Any]:
    return provider_outcome_learning_service.scorecard(
        provider_id=request.provider_id,
        task_tag=request.task_tag,
    )


@router.post("/router-hints")
def router_hints(request: RouterHintsRequest) -> dict[str, Any]:
    return provider_outcome_learning_service.router_hints(
        task_tags=request.task_tags,
        sensitive=request.sensitive,
    )


@router.post("/simulate-route")
def simulate_route(request: SimulateRouteRequest) -> dict[str, Any]:
    return provider_outcome_learning_service.simulate_route(
        goal=request.goal,
        task_tags=request.task_tags,
        sensitive=request.sensitive,
        needs_code=request.needs_code,
        needs_large_context=request.needs_large_context,
        needs_multimodal=request.needs_multimodal,
    )


@router.get("/latest")
@router.post("/latest")
def latest() -> dict[str, Any]:
    return provider_outcome_learning_service.latest()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return provider_outcome_learning_service.package()
