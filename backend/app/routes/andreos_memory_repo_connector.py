from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.andreos_memory_repo_connector_service import (
    andreos_memory_repo_connector_service,
)


router = APIRouter(
    prefix="/api/andreos-memory-repo",
    tags=["andreos-memory-repo"],
)


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return andreos_memory_repo_connector_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return andreos_memory_repo_connector_service.panel()


@router.get("/structure")
@router.post("/structure")
def structure() -> dict[str, Any]:
    return andreos_memory_repo_connector_service.structure()


@router.get("/audit")
@router.post("/audit")
async def audit() -> dict[str, Any]:
    return await andreos_memory_repo_connector_service.audit()


@router.get("/seed-plan")
@router.post("/seed-plan")
def seed_plan() -> dict[str, Any]:
    return andreos_memory_repo_connector_service.seed_plan()


@router.get("/project/{project_id}")
async def read_project(project_id: str) -> dict[str, Any]:
    return await andreos_memory_repo_connector_service.read_project(project_id)


@router.get("/handoff-prompt/{project_id}")
def handoff_prompt(project_id: str) -> dict[str, Any]:
    return andreos_memory_repo_connector_service.handoff_prompt(project_id)


@router.get("/package")
@router.post("/package")
async def package() -> dict[str, Any]:
    return await andreos_memory_repo_connector_service.package()
