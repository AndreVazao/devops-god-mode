from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_env_writers_dry_run_service import provider_env_writers_dry_run_service

router = APIRouter(prefix="/api/provider-env-writers-dry-run", tags=["provider-env-writers-dry-run"])


class CreateGateRequest(BaseModel):
    plan_id: str
    provider: str
    purpose: str = "Build provider env dry-run payload"


class BuildFromPlanRequest(BaseModel):
    plan_id: str
    approved_gate_id: str
    passphrase: str
    provider: str | None = None


class BuildFromPreviewRequest(BaseModel):
    preview: dict[str, Any]
    approved_gate_id: str
    provider: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return provider_env_writers_dry_run_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return provider_env_writers_dry_run_service.policy()


@router.post("/create-gate")
def create_gate(payload: CreateGateRequest) -> dict[str, Any]:
    return provider_env_writers_dry_run_service.create_dry_run_gate(
        plan_id=payload.plan_id,
        provider=payload.provider,
        purpose=payload.purpose,
    )


@router.post("/build-from-plan")
def build_from_plan(payload: BuildFromPlanRequest) -> dict[str, Any]:
    return provider_env_writers_dry_run_service.build_from_injection_plan(
        plan_id=payload.plan_id,
        approved_gate_id=payload.approved_gate_id,
        passphrase=payload.passphrase,
        provider=payload.provider,
    )


@router.post("/build-from-preview")
def build_from_preview(payload: BuildFromPreviewRequest) -> dict[str, Any]:
    return provider_env_writers_dry_run_service.build_from_apply_preview(
        preview=payload.preview,
        approved_gate_id=payload.approved_gate_id,
        provider=payload.provider,
    )


@router.get("/writer-specs")
@router.post("/writer-specs")
def writer_specs() -> dict[str, Any]:
    return provider_env_writers_dry_run_service.writer_specs()


@router.get("/dry-runs")
@router.post("/dry-runs")
def dry_runs(limit: int = 50) -> dict[str, Any]:
    return provider_env_writers_dry_run_service.list_dry_runs(limit=limit)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return provider_env_writers_dry_run_service.package()
