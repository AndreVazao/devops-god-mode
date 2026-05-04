from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.god_mode_reality_audit_service import god_mode_reality_audit_service

router = APIRouter(prefix="/api/god-mode-reality-audit", tags=["god-mode-reality-audit"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return god_mode_reality_audit_service.status()


@router.get("/audit")
@router.post("/audit")
def audit() -> dict[str, Any]:
    return god_mode_reality_audit_service.audit()


@router.get("/capabilities")
@router.post("/capabilities")
def capabilities() -> dict[str, Any]:
    return {"ok": True, "capabilities": god_mode_reality_audit_service.capabilities()}


@router.get("/first-install-mission")
@router.post("/first-install-mission")
def first_install_mission() -> dict[str, Any]:
    return {"ok": True, "mission": god_mode_reality_audit_service.first_install_mission()}


@router.get("/project-tree-and-inventory-mission")
@router.post("/project-tree-and-inventory-mission")
def project_tree_and_inventory_mission() -> dict[str, Any]:
    return {"ok": True, "mission": god_mode_reality_audit_service.project_tree_and_inventory_mission()}


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return god_mode_reality_audit_service.package()
