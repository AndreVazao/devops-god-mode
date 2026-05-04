from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.home_app_control_surface_service import home_app_control_surface_service

router = APIRouter(prefix="/api/home-control-surface", tags=["home-control-surface"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return home_app_control_surface_service.status()


@router.get("/panel")
@router.post("/panel")
def panel() -> dict[str, Any]:
    return home_app_control_surface_service.panel()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return home_app_control_surface_service.policy()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return {"ok": True, "rules": home_app_control_surface_service.rules()}


@router.get("/modules")
@router.post("/modules")
def modules() -> dict[str, Any]:
    return {"ok": True, "modules": home_app_control_surface_service.modules()}


@router.get("/buttons")
@router.post("/buttons")
def buttons() -> dict[str, Any]:
    return home_app_control_surface_service.button_manifest()


@router.get("/quick-start")
@router.post("/quick-start")
def quick_start() -> dict[str, Any]:
    return home_app_control_surface_service.quick_start()


@router.get("/mobile-shell")
@router.post("/mobile-shell")
def mobile_shell() -> dict[str, Any]:
    return home_app_control_surface_service.mobile_shell_manifest()


@router.get("/desktop-shell")
@router.post("/desktop-shell")
def desktop_shell() -> dict[str, Any]:
    return home_app_control_surface_service.desktop_shell_manifest()


@router.get("/latest")
@router.post("/latest")
def latest() -> dict[str, Any]:
    return home_app_control_surface_service.latest()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return home_app_control_surface_service.package()
