from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.guided_provider_setup_wizard_service import guided_provider_setup_wizard_service

router = APIRouter(prefix="/api/guided-provider-setup", tags=["guided-provider-setup"])


class StartSetupPayload(BaseModel):
    provider: str = "tailscale"
    tenant_id: str = "owner-andre"


class CaptureResultPayload(BaseModel):
    setup_session_id: str
    values: dict[str, Any]
    store_remote_profile: bool = True
    store_sensitive_material_in_vault: bool = False
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return guided_provider_setup_wizard_service.status()


@router.get("/providers")
@router.post("/providers")
def providers() -> dict[str, Any]:
    return guided_provider_setup_wizard_service.providers()


@router.post("/start")
def start_setup(payload: StartSetupPayload) -> dict[str, Any]:
    return guided_provider_setup_wizard_service.start_setup(
        provider=payload.provider,
        tenant_id=payload.tenant_id,
    )


@router.post("/capture-result")
def capture_result(payload: CaptureResultPayload) -> dict[str, Any]:
    return guided_provider_setup_wizard_service.capture_result(
        setup_session_id=payload.setup_session_id,
        values=payload.values,
        store_remote_profile=payload.store_remote_profile,
        store_sensitive_material_in_vault=payload.store_sensitive_material_in_vault,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return guided_provider_setup_wizard_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return guided_provider_setup_wizard_service.package()
