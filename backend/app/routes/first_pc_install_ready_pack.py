from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.first_pc_install_ready_pack_service import first_pc_install_ready_pack_service

router = APIRouter(prefix="/api/first-pc-install-ready-pack", tags=["first-pc-install-ready-pack"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return first_pc_install_ready_pack_service.status()


@router.get("/one-click-local-start-contract")
@router.post("/one-click-local-start-contract")
def one_click_local_start_contract() -> dict[str, Any]:
    return first_pc_install_ready_pack_service.one_click_local_start_contract()


@router.get("/ready-pack")
@router.post("/ready-pack")
def ready_pack() -> dict[str, Any]:
    return first_pc_install_ready_pack_service.readiness_pack()


@router.get("/checklist")
@router.post("/checklist")
def checklist() -> dict[str, Any]:
    return first_pc_install_ready_pack_service.checklist()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return first_pc_install_ready_pack_service.package()
