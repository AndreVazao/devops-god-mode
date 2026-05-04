from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.god_mode_global_state_service import god_mode_global_state_service

router = APIRouter(prefix="/api/god-mode-global-state", tags=["god-mode-global-state"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return god_mode_global_state_service.status()


@router.get("/phases")
@router.post("/phases")
def phases() -> dict[str, Any]:
    return {"ok": True, "phases": god_mode_global_state_service.implemented_phases()}


@router.get("/operating-model")
@router.post("/operating-model")
def operating_model() -> dict[str, Any]:
    return {"ok": True, "operating_model": god_mode_global_state_service.operating_model()}


@router.get("/memory-model")
@router.post("/memory-model")
def memory_model() -> dict[str, Any]:
    return {"ok": True, "memory_model": god_mode_global_state_service.memory_model()}


@router.get("/vault-policy")
@router.post("/vault-policy")
def vault_policy() -> dict[str, Any]:
    return {"ok": True, "vault_policy": god_mode_global_state_service.vault_policy()}


@router.get("/self-update-model")
@router.post("/self-update-model")
def self_update_model() -> dict[str, Any]:
    return {"ok": True, "self_update_model": god_mode_global_state_service.self_update_model()}


@router.get("/backlog")
@router.post("/backlog")
def backlog() -> dict[str, Any]:
    return {"ok": True, "backlog": god_mode_global_state_service.backlog()}


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return god_mode_global_state_service.package()
