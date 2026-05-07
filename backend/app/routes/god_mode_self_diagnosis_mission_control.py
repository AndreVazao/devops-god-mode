from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.god_mode_self_diagnosis_mission_control_service import god_mode_self_diagnosis_mission_control_service

router = APIRouter(prefix="/api/god-mode-self-diagnosis", tags=["god-mode-self-diagnosis"])


class RunDiagnosisPayload(BaseModel):
    tenant_id: str = "owner-andre"
    focus: str = "install_first_then_self_evolve"


class UpdateQueuePayload(BaseModel):
    self_fix_queue_item_id: str
    status: str
    note: str = ""
    tenant_id: str = "owner-andre"


class PlanningBriefPayload(BaseModel):
    self_fix_queue_item_id: str
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.policy()


@router.post("/run")
def run_diagnosis(payload: RunDiagnosisPayload) -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.run_diagnosis(
        tenant_id=payload.tenant_id,
        focus=payload.focus,
    )


@router.get("/queue")
def queue(status: str | None = None, severity: str | None = None, install_blocker: bool | None = None, limit: int = 100) -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.list_queue(
        status=status,
        severity=severity,
        install_blocker=install_blocker,
        limit=limit,
    )


@router.post("/update-queue-item")
def update_queue_item(payload: UpdateQueuePayload) -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.update_queue_item(
        self_fix_queue_item_id=payload.self_fix_queue_item_id,
        status=payload.status,
        note=payload.note,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-pr-planning-brief")
def create_pr_planning_brief(payload: PlanningBriefPayload) -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.create_pr_planning_brief(
        self_fix_queue_item_id=payload.self_fix_queue_item_id,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return god_mode_self_diagnosis_mission_control_service.package()
