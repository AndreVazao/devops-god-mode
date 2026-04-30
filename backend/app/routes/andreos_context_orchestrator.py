from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.services.andreos_context_orchestrator_service import andreos_context_orchestrator_service


router = APIRouter(prefix="/api/andreos-context", tags=["andreos-context"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return andreos_context_orchestrator_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return andreos_context_orchestrator_service.panel()


@router.get("/topology")
@router.post("/topology")
def topology() -> dict[str, Any]:
    return andreos_context_orchestrator_service.topology()


@router.get("/readiness")
@router.post("/readiness")
async def readiness() -> dict[str, Any]:
    return await andreos_context_orchestrator_service.readiness()


@router.get("/context/{project_id}")
async def context_pack(project_id: str, max_chars: int = Query(default=6000)) -> dict[str, Any]:
    return await andreos_context_orchestrator_service.context_pack(project_id=project_id, max_chars=max_chars)


@router.get("/brief/{project_id}")
async def brief(project_id: str, target: str = Query(default="chatgpt")) -> dict[str, Any]:
    return await andreos_context_orchestrator_service.provider_brief(project_id=project_id, provider=target)


@router.get("/sync-plan/{project_id}")
def sync_plan(project_id: str) -> dict[str, Any]:
    return andreos_context_orchestrator_service.sync_plan(project_id)


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return andreos_context_orchestrator_service.intake_policy()


@router.get("/package")
@router.post("/package")
async def package(project_id: str = Query(default="GOD_MODE")) -> dict[str, Any]:
    return await andreos_context_orchestrator_service.package(project_id=project_id)
