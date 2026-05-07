from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.native_skills_adoption_queue_service import native_skills_adoption_queue_service

router = APIRouter(prefix="/api/native-skills-adoption-queue", tags=["native-skills-adoption-queue"])


class PromoteCandidatePayload(BaseModel):
    candidate_id: str
    target_project: str = "GOD_MODE"
    priority: str = "normal"
    operator_note: str = ""
    tenant_id: str = "owner-andre"


class PromoteFilterPayload(BaseModel):
    domain: str | None = None
    risk: str | None = None
    limit: int = 25
    target_project: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


class StatusPayload(BaseModel):
    adoption_queue_item_id: str
    new_status: str
    reason: str = ""
    tenant_id: str = "owner-andre"


class ImplementationPlanPayload(BaseModel):
    adoption_queue_item_id: str
    target_module_hint: str = ""
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return native_skills_adoption_queue_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return native_skills_adoption_queue_service.policy()


@router.post("/promote-candidate")
def promote_candidate(payload: PromoteCandidatePayload) -> dict[str, Any]:
    return native_skills_adoption_queue_service.promote_candidate(
        candidate_id=payload.candidate_id,
        target_project=payload.target_project,
        priority=payload.priority,
        operator_note=payload.operator_note,
        tenant_id=payload.tenant_id,
    )


@router.post("/promote-candidates-by-filter")
def promote_candidates_by_filter(payload: PromoteFilterPayload) -> dict[str, Any]:
    return native_skills_adoption_queue_service.promote_candidates_by_filter(
        domain=payload.domain,
        risk=payload.risk,
        limit=payload.limit,
        target_project=payload.target_project,
        tenant_id=payload.tenant_id,
    )


@router.get("/queue")
def queue(status: str | None = None, domain: str | None = None, risk: str | None = None, limit: int = 100) -> dict[str, Any]:
    return native_skills_adoption_queue_service.list_queue(status=status, domain=domain, risk=risk, limit=limit)


@router.post("/update-status")
def update_status(payload: StatusPayload) -> dict[str, Any]:
    return native_skills_adoption_queue_service.update_status(
        adoption_queue_item_id=payload.adoption_queue_item_id,
        new_status=payload.new_status,
        reason=payload.reason,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-implementation-plan")
def create_implementation_plan(payload: ImplementationPlanPayload) -> dict[str, Any]:
    return native_skills_adoption_queue_service.create_implementation_plan(
        adoption_queue_item_id=payload.adoption_queue_item_id,
        target_module_hint=payload.target_module_hint,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return native_skills_adoption_queue_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return native_skills_adoption_queue_service.package()
