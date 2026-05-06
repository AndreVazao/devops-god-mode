from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.external_lab_snapshot_reader_service import external_lab_snapshot_reader_service

router = APIRouter(prefix="/api/external-lab-snapshot-reader", tags=["external-lab-snapshot-reader"])


class SnapshotTextPayload(BaseModel):
    lab_id: str
    lab_repo_full_name: str
    snapshot_text: str
    operator_goal: str = ""
    tenant_id: str = "owner-andre"


class SnapshotPayload(BaseModel):
    lab_id: str
    lab_repo_full_name: str
    snapshot: dict[str, Any]
    operator_goal: str = ""
    tenant_id: str = "owner-andre"


class RegistryCandidatePayload(BaseModel):
    operator_goal: str = ""
    tenant_id: str = "owner-andre"


class CandidatePlanPayload(BaseModel):
    candidate_id: str
    target_project: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return external_lab_snapshot_reader_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return external_lab_snapshot_reader_service.policy()


@router.post("/ingest-snapshot-text")
def ingest_snapshot_text(payload: SnapshotTextPayload) -> dict[str, Any]:
    return external_lab_snapshot_reader_service.ingest_snapshot_text(
        lab_id=payload.lab_id,
        lab_repo_full_name=payload.lab_repo_full_name,
        snapshot_text=payload.snapshot_text,
        operator_goal=payload.operator_goal,
        tenant_id=payload.tenant_id,
    )


@router.post("/ingest-snapshot")
def ingest_snapshot(payload: SnapshotPayload) -> dict[str, Any]:
    return external_lab_snapshot_reader_service.ingest_snapshot(
        lab_id=payload.lab_id,
        lab_repo_full_name=payload.lab_repo_full_name,
        snapshot=payload.snapshot,
        operator_goal=payload.operator_goal,
        tenant_id=payload.tenant_id,
    )


@router.post("/generate-candidates-from-registry")
def generate_candidates_from_registry(payload: RegistryCandidatePayload) -> dict[str, Any]:
    return external_lab_snapshot_reader_service.generate_candidates_from_registry(
        operator_goal=payload.operator_goal,
        tenant_id=payload.tenant_id,
    )


@router.get("/candidates")
def candidates(domain: str | None = None, risk: str | None = None, limit: int = 100) -> dict[str, Any]:
    return external_lab_snapshot_reader_service.list_candidates(domain=domain, risk=risk, limit=limit)


@router.post("/create-candidate-plan")
def create_candidate_plan(payload: CandidatePlanPayload) -> dict[str, Any]:
    return external_lab_snapshot_reader_service.create_candidate_plan(
        candidate_id=payload.candidate_id,
        target_project=payload.target_project,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return external_lab_snapshot_reader_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return external_lab_snapshot_reader_service.package()
