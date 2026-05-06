from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_browser_local_launcher_service import provider_browser_local_launcher_service

router = APIRouter(prefix="/api/provider-browser-local-launcher", tags=["provider-browser-local-launcher"])


class LaunchContractRequest(BaseModel):
    provider_id: str
    project_hint: str = "GOD_MODE"
    plan_id: str | None = None
    tenant_id: str = "owner-andre"
    purpose: str = "manual provider proof/capture"


class CaptureContractRequest(BaseModel):
    launch_contract_id: str
    title: str = "Provider captured conversation"
    provider: str | None = None
    project_hint: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


class ImportCaptureRequest(BaseModel):
    capture_contract_id: str
    transcript_text: str
    tenant_id: str = "owner-andre"
    create_review_card: bool = True


class AttentionCardRequest(BaseModel):
    launch_contract_id: str
    tenant_id: str = "owner-andre"


class ProviderPackageRequest(BaseModel):
    provider_id: str
    project_hint: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return provider_browser_local_launcher_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return provider_browser_local_launcher_service.policy()


@router.post("/create-launch-contract")
def create_launch_contract(payload: LaunchContractRequest) -> dict[str, Any]:
    return provider_browser_local_launcher_service.create_launch_contract(
        provider_id=payload.provider_id,
        project_hint=payload.project_hint,
        plan_id=payload.plan_id,
        tenant_id=payload.tenant_id,
        purpose=payload.purpose,
    )


@router.post("/create-capture-contract")
def create_capture_contract(payload: CaptureContractRequest) -> dict[str, Any]:
    return provider_browser_local_launcher_service.create_capture_contract(
        launch_contract_id=payload.launch_contract_id,
        title=payload.title,
        provider=payload.provider,
        project_hint=payload.project_hint,
        tenant_id=payload.tenant_id,
    )


@router.post("/import-capture")
def import_capture(payload: ImportCaptureRequest) -> dict[str, Any]:
    return provider_browser_local_launcher_service.import_capture(
        capture_contract_id=payload.capture_contract_id,
        transcript_text=payload.transcript_text,
        tenant_id=payload.tenant_id,
        create_review_card=payload.create_review_card,
    )


@router.post("/create-attention-card")
def create_attention_card(payload: AttentionCardRequest) -> dict[str, Any]:
    return provider_browser_local_launcher_service.create_attention_card(
        launch_contract_id=payload.launch_contract_id,
        tenant_id=payload.tenant_id,
    )


@router.post("/package-provider")
def package_provider(payload: ProviderPackageRequest) -> dict[str, Any]:
    return provider_browser_local_launcher_service.package_for_provider(
        provider_id=payload.provider_id,
        project_hint=payload.project_hint,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return provider_browser_local_launcher_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return provider_browser_local_launcher_service.package()
