from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.obsidian_technical_sync_service import obsidian_technical_sync_service


router = APIRouter(prefix="/api/obsidian-technical-sync", tags=["obsidian-technical-sync"])


class ClassifyRequest(BaseModel):
    title: str
    body: str | None = None
    project: str | None = None
    repo: str | None = None


class PrepareSyncRequest(BaseModel):
    title: str
    body: str
    project: str
    repo: str | None = None
    source_obsidian_path: str | None = None
    target_github_memory_path: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return obsidian_technical_sync_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return obsidian_technical_sync_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": obsidian_technical_sync_service.rules()}


@router.post("/classify")
def classify(request: ClassifyRequest) -> dict[str, Any]:
    return obsidian_technical_sync_service.classify(
        title=request.title,
        body=request.body,
        project=request.project,
        repo=request.repo,
    )


@router.get("/template")
def template(project: str = "GOD_MODE") -> dict[str, Any]:
    return obsidian_technical_sync_service.template(project=project)


@router.post("/prepare-sync")
def prepare_sync(request: PrepareSyncRequest) -> dict[str, Any]:
    return obsidian_technical_sync_service.prepare_sync(
        title=request.title,
        body=request.body,
        project=request.project,
        repo=request.repo,
        source_obsidian_path=request.source_obsidian_path,
        target_github_memory_path=request.target_github_memory_path,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return {
        "status": obsidian_technical_sync_service.status(),
        "panel": obsidian_technical_sync_service.panel(),
        "rules": obsidian_technical_sync_service.rules(),
        "template": obsidian_technical_sync_service.template(),
    }
