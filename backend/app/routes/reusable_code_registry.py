from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.reusable_code_registry_service import reusable_code_registry_service


router = APIRouter(prefix="/api/reusable-code-registry", tags=["reusable-code-registry"])


class RegisterAssetRequest(BaseModel):
    purpose: str
    repo: str
    files: list[str] = Field(default_factory=list)
    project: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    aliases: list[str] | None = None
    status: str = "available"
    notes: str | None = None


class SearchRequest(BaseModel):
    query: str
    project: str | None = None
    limit: int = Field(default=10, ge=1, le=50)


class MarkReusedRequest(BaseModel):
    asset_id: str
    target_project: str
    target_repo: str | None = None
    notes: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return reusable_code_registry_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return reusable_code_registry_service.panel()


@router.get("/assets")
def assets(
    limit: int = Query(default=100, ge=1, le=500),
    tag: str | None = Query(default=None),
    project: str | None = Query(default=None),
) -> dict[str, Any]:
    return reusable_code_registry_service.assets(limit=limit, tag=tag, project=project)


@router.post("/register")
def register(request: RegisterAssetRequest) -> dict[str, Any]:
    return reusable_code_registry_service.register(
        purpose=request.purpose,
        repo=request.repo,
        files=request.files,
        project=request.project,
        description=request.description,
        tags=request.tags,
        aliases=request.aliases,
        status=request.status,
        notes=request.notes,
    )


@router.post("/search")
def search(request: SearchRequest) -> dict[str, Any]:
    return reusable_code_registry_service.search(
        query=request.query,
        project=request.project,
        limit=request.limit,
    )


@router.post("/mark-reused")
def mark_reused(request: MarkReusedRequest) -> dict[str, Any]:
    return reusable_code_registry_service.mark_reused(
        asset_id=request.asset_id,
        target_project=request.target_project,
        target_repo=request.target_repo,
        notes=request.notes,
    )


@router.post("/seed")
def seed() -> dict[str, Any]:
    return reusable_code_registry_service.import_seed_assets()


@router.get("/markdown")
def markdown() -> dict[str, Any]:
    return reusable_code_registry_service.export_markdown()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return reusable_code_registry_service.package()
