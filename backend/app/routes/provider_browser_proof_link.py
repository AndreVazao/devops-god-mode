from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.provider_browser_proof_link_service import provider_browser_proof_link_service

router = APIRouter(prefix="/api/provider-browser-proof-link", tags=["provider-browser-proof-link"])


class PlanRequest(BaseModel):
    plan_id: str
    tenant_id: str = "owner-andre"


class GateRequest(BaseModel):
    plan_id: str
    provider_id: str
    tenant_id: str = "owner-andre"
    purpose: str = "future browser proof automation"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return provider_browser_proof_link_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return provider_browser_proof_link_service.policy()


@router.post("/build-links")
def build_links(payload: PlanRequest) -> dict[str, Any]:
    return provider_browser_proof_link_service.build_links_for_plan(plan_id=payload.plan_id, tenant_id=payload.tenant_id)


@router.post("/create-login-cards")
def create_login_cards(payload: PlanRequest) -> dict[str, Any]:
    return provider_browser_proof_link_service.create_login_attention_cards(plan_id=payload.plan_id, tenant_id=payload.tenant_id)


@router.post("/create-automation-gate")
def create_automation_gate(payload: GateRequest) -> dict[str, Any]:
    return provider_browser_proof_link_service.create_browser_automation_gate(
        plan_id=payload.plan_id,
        provider_id=payload.provider_id,
        tenant_id=payload.tenant_id,
        purpose=payload.purpose,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard(plan_id: str | None = None) -> dict[str, Any]:
    return provider_browser_proof_link_service.dashboard(plan_id=plan_id)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return provider_browser_proof_link_service.package()
