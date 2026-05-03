from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.orchestration_playbook_service import orchestration_playbook_service


router = APIRouter(prefix="/api/orchestration-playbooks", tags=["orchestration-playbooks"])


class PlaybookRequest(BaseModel):
    playbook: dict[str, Any] = Field(default_factory=dict)
    goal_id: str | None = None
    operator_approved: bool = False
    simulate: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return orchestration_playbook_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return orchestration_playbook_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": orchestration_playbook_service.rules()}


@router.get("/template")
def template(kind: str = Query(default="safe_feature")) -> dict[str, Any]:
    return orchestration_playbook_service.template(kind=kind)


@router.post("/validate")
def validate(request: PlaybookRequest) -> dict[str, Any]:
    return orchestration_playbook_service.validate(playbook=request.playbook)


@router.post("/to-pipeline")
def to_pipeline(request: PlaybookRequest) -> dict[str, Any]:
    return orchestration_playbook_service.to_pipeline_request(
        playbook=request.playbook,
        goal_id=request.goal_id,
        operator_approved=request.operator_approved,
    )


@router.post("/run")
def run(request: PlaybookRequest) -> dict[str, Any]:
    return orchestration_playbook_service.run(
        playbook=request.playbook,
        goal_id=request.goal_id,
        operator_approved=request.operator_approved,
        simulate=request.simulate,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return orchestration_playbook_service.package()
