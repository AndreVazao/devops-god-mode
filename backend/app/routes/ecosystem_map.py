from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.ecosystem_map_service import ecosystem_map_service


router = APIRouter(prefix="/api/ecosystem-map", tags=["ecosystem-map"])


class ClassifyProjectRequest(BaseModel):
    name: str
    description: str | None = None
    repo: str | None = None
    is_cloud: bool | None = None
    is_mobile: bool | None = None


class ReusableDecisionRequest(BaseModel):
    purpose: str
    source_project: str | None = None
    source_repo: str | None = None
    files: list[str] = Field(default_factory=list)


class ArchiveDecisionRequest(BaseModel):
    project_name: str
    has_repo: bool = True
    has_reusable_code: bool = False
    is_replaced: bool = False
    is_validated: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return ecosystem_map_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return ecosystem_map_service.panel()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": ecosystem_map_service.rules()}


@router.get("/groups")
def groups() -> dict[str, Any]:
    return ecosystem_map_service.groups()


@router.get("/repos")
def repos() -> dict[str, Any]:
    return ecosystem_map_service.repos()


@router.get("/classify")
def classify_get(
    name: str = Query(...),
    description: str | None = Query(default=None),
    repo: str | None = Query(default=None),
    is_cloud: bool | None = Query(default=None),
    is_mobile: bool | None = Query(default=None),
) -> dict[str, Any]:
    return ecosystem_map_service.classify(
        name=name,
        description=description,
        repo=repo,
        is_cloud=is_cloud,
        is_mobile=is_mobile,
    )


@router.post("/classify")
def classify_post(request: ClassifyProjectRequest) -> dict[str, Any]:
    return ecosystem_map_service.classify(
        name=request.name,
        description=request.description,
        repo=request.repo,
        is_cloud=request.is_cloud,
        is_mobile=request.is_mobile,
    )


@router.post("/reusable-decision")
def reusable_decision(request: ReusableDecisionRequest) -> dict[str, Any]:
    return ecosystem_map_service.reusable_decision(
        purpose=request.purpose,
        source_project=request.source_project,
        source_repo=request.source_repo,
        files=request.files,
    )


@router.post("/archive-decision")
def archive_decision(request: ArchiveDecisionRequest) -> dict[str, Any]:
    return ecosystem_map_service.archive_decision(
        project_name=request.project_name,
        has_repo=request.has_repo,
        has_reusable_code=request.has_reusable_code,
        is_replaced=request.is_replaced,
        is_validated=request.is_validated,
    )


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return ecosystem_map_service.package()
