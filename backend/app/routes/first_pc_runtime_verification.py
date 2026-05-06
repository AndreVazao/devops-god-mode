from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.services.first_pc_runtime_verification_service import first_pc_runtime_verification_service

router = APIRouter(prefix="/api/first-pc-runtime-verification", tags=["first-pc-runtime-verification"])


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return first_pc_runtime_verification_service.status()


@router.get("/guide")
@router.post("/guide")
def guide() -> dict[str, Any]:
    return first_pc_runtime_verification_service.first_run_guide()


@router.get("/checks")
@router.post("/checks")
def checks() -> dict[str, Any]:
    return first_pc_runtime_verification_service.runtime_checks()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return first_pc_runtime_verification_service.package()
