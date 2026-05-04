from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.memory_sync_runtime_service import memory_sync_runtime_service

router = APIRouter(prefix="/api/memory-sync-runtime", tags=["memory-sync-runtime"])


class RegisterMergedPhaseRequest(BaseModel):
    phase_number: int
    phase_title: str
    repo_full_name: str
    pr_number: int
    merge_commit: str
    summary: str
    validation: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    next_phase: str | None = None
    project_name: str = "GOD_MODE"


class BuildPackageRequest(BaseModel):
    event_id: str
    include_obsidian_note: bool = True


class PrepareObsidianNoteRequest(BaseModel):
    event_id: str


class SyncStablePackageRequest(BaseModel):
    package_id: str
    dry_run: bool = True
    memory_repo: str = "AndreVazao/andreos-memory"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return memory_sync_runtime_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return memory_sync_runtime_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return memory_sync_runtime_service.policy()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": memory_sync_runtime_service.rules()}


@router.post("/register-merged-phase")
def register_merged_phase(request: RegisterMergedPhaseRequest) -> dict[str, Any]:
    return memory_sync_runtime_service.register_merged_phase(
        phase_number=request.phase_number,
        phase_title=request.phase_title,
        repo_full_name=request.repo_full_name,
        pr_number=request.pr_number,
        merge_commit=request.merge_commit,
        summary=request.summary,
        validation=request.validation,
        decisions=request.decisions,
        next_phase=request.next_phase,
        project_name=request.project_name,
    )


@router.post("/build-package")
def build_package(request: BuildPackageRequest) -> dict[str, Any]:
    return memory_sync_runtime_service.build_package(
        event_id=request.event_id,
        include_obsidian_note=request.include_obsidian_note,
    )


@router.post("/prepare-obsidian-note")
def prepare_obsidian_note(request: PrepareObsidianNoteRequest) -> dict[str, Any]:
    return memory_sync_runtime_service.prepare_obsidian_note(event_id=request.event_id)


@router.post("/sync-stable")
async def sync_stable(request: SyncStablePackageRequest) -> dict[str, Any]:
    return await memory_sync_runtime_service.sync_stable_package(
        package_id=request.package_id,
        dry_run=request.dry_run,
        memory_repo=request.memory_repo,
    )


@router.post("/preview-merged-phase")
def preview_merged_phase(request: RegisterMergedPhaseRequest) -> dict[str, Any]:
    return memory_sync_runtime_service.end_to_end_preview(
        phase_number=request.phase_number,
        phase_title=request.phase_title,
        repo_full_name=request.repo_full_name,
        pr_number=request.pr_number,
        merge_commit=request.merge_commit,
        summary=request.summary,
        validation=request.validation,
        decisions=request.decisions,
        next_phase=request.next_phase,
        project_name=request.project_name,
    )


@router.get("/latest")
@router.post("/latest")
def latest() -> dict[str, Any]:
    return memory_sync_runtime_service.latest()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return memory_sync_runtime_service.package()
