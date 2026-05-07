from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.final_install_use_pack_service import final_install_use_pack_service

router = APIRouter(prefix="/api/final-install-use", tags=["final-install-use"])


class StartPayload(BaseModel):
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return final_install_use_pack_service.status()


@router.get("/readiness")
@router.post("/readiness")
def readiness() -> dict[str, Any]:
    return final_install_use_pack_service.final_readiness()


@router.get("/apk-endpoint-contract")
@router.post("/apk-endpoint-contract")
def apk_endpoint_contract() -> dict[str, Any]:
    return final_install_use_pack_service.apk_endpoint_contract()


@router.get("/install-steps")
@router.post("/install-steps")
def install_steps() -> dict[str, Any]:
    return final_install_use_pack_service.install_steps()


@router.post("/start-now")
def start_now(payload: StartPayload) -> dict[str, Any]:
    return final_install_use_pack_service.start_now(tenant_id=payload.tenant_id)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return final_install_use_pack_service.package()
