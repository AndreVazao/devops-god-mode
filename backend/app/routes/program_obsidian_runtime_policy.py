from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.program_obsidian_runtime_policy_service import program_obsidian_runtime_policy_service


router = APIRouter(prefix="/api/program-obsidian-policy", tags=["program-obsidian-policy"])


class ClassifyProgramUseRequest(BaseModel):
    program_name: str
    is_cloud: bool = False
    is_god_mode: bool = False
    requested_use: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return program_obsidian_runtime_policy_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return program_obsidian_runtime_policy_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": program_obsidian_runtime_policy_service.rules()}


@router.get("/program-classes")
@router.post("/program-classes")
def program_classes() -> dict[str, Any]:
    return {"ok": True, "program_classes": program_obsidian_runtime_policy_service.program_classes()}


@router.post("/classify")
def classify(request: ClassifyProgramUseRequest) -> dict[str, Any]:
    return program_obsidian_runtime_policy_service.classify_program_use(
        program_name=request.program_name,
        is_cloud=request.is_cloud,
        is_god_mode=request.is_god_mode,
        requested_use=request.requested_use,
    )


@router.get("/examples")
@router.post("/examples")
def examples() -> dict[str, Any]:
    return {"ok": True, "examples": program_obsidian_runtime_policy_service.examples()}


@router.get("/handoff-note")
@router.post("/handoff-note")
def handoff_note() -> dict[str, Any]:
    return program_obsidian_runtime_policy_service.handoff_note()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return program_obsidian_runtime_policy_service.package()
