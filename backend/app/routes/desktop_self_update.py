from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.desktop_self_update_service import desktop_self_update_service


router = APIRouter(prefix="/api/desktop-self-update", tags=["desktop-self-update"])


class CompareUpdateRequest(BaseModel):
    latest_version: str | None = None
    latest_phase: str | None = None


class PrepareLocalPackageUpdateRequest(BaseModel):
    package_path: str
    target_version: str
    target_phase: str | None = None
    notes: str | None = None


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return desktop_self_update_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return desktop_self_update_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return desktop_self_update_service.policy()


@router.get("/manifest")
@router.post("/manifest")
def manifest() -> dict[str, Any]:
    return desktop_self_update_service.manifest()


@router.post("/compare")
def compare(request: CompareUpdateRequest) -> dict[str, Any]:
    return desktop_self_update_service.compare(
        latest_version=request.latest_version,
        latest_phase=request.latest_phase,
    )


@router.post("/prepare-local-package")
def prepare_local_package(request: PrepareLocalPackageUpdateRequest) -> dict[str, Any]:
    return desktop_self_update_service.prepare_local_package_update(
        package_path=request.package_path,
        target_version=request.target_version,
        target_phase=request.target_phase,
        notes=request.notes,
    )


@router.post("/clear-pending")
def clear_pending() -> dict[str, Any]:
    return desktop_self_update_service.clear_pending_update()


@router.get("/package")
@router.post("/package")
async def package() -> dict[str, Any]:
    return await desktop_self_update_service.package()
