from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.vault_deployment_binding_service import vault_deployment_binding_service

router = APIRouter(prefix="/api/vault-deployment-binding", tags=["vault-deployment-binding"])


class CreateBindingRequest(BaseModel):
    secret_ref_id: str
    target_project: str
    target_provider: str
    environment: str
    inject_as: str
    provider_mode: str = "manual_export"
    provider_target_id: str | None = None
    notes: str | None = None


class ContractBindingRequest(BaseModel):
    report_id: str | None = None
    target_provider: str = "manual"
    provider_mode: str = "manual_export"


class BuildPlanRequest(BaseModel):
    target_project: str
    environment: str
    target_provider: str | None = None


class ApplyGateRequest(BaseModel):
    plan_id: str
    purpose: str = "Apply vault env injection plan"


class ApplyPreviewRequest(BaseModel):
    plan_id: str
    approved_gate_id: str
    passphrase: str
    reveal_values: bool = False


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return vault_deployment_binding_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return vault_deployment_binding_service.policy()


@router.post("/create-binding")
def create_binding(payload: CreateBindingRequest) -> dict[str, Any]:
    return vault_deployment_binding_service.create_binding(
        secret_ref_id=payload.secret_ref_id,
        target_project=payload.target_project,
        target_provider=payload.target_provider,
        environment=payload.environment,
        inject_as=payload.inject_as,
        provider_mode=payload.provider_mode,
        provider_target_id=payload.provider_target_id,
        notes=payload.notes,
    )


@router.post("/create-bindings-from-contract")
def create_bindings_from_contract(payload: ContractBindingRequest) -> dict[str, Any]:
    return vault_deployment_binding_service.create_bindings_from_contract_report(
        report_id=payload.report_id,
        target_provider=payload.target_provider,
        provider_mode=payload.provider_mode,
    )


@router.post("/build-injection-plan")
def build_injection_plan(payload: BuildPlanRequest) -> dict[str, Any]:
    return vault_deployment_binding_service.build_injection_plan(
        target_project=payload.target_project,
        environment=payload.environment,
        target_provider=payload.target_provider,
    )


@router.post("/create-apply-gate")
def create_apply_gate(payload: ApplyGateRequest) -> dict[str, Any]:
    return vault_deployment_binding_service.create_apply_gate(plan_id=payload.plan_id, purpose=payload.purpose)


@router.post("/apply-preview")
def apply_preview(payload: ApplyPreviewRequest) -> dict[str, Any]:
    return vault_deployment_binding_service.build_apply_preview(
        plan_id=payload.plan_id,
        approved_gate_id=payload.approved_gate_id,
        passphrase=payload.passphrase,
        reveal_values=payload.reveal_values,
    )


@router.get("/bindings")
@router.post("/bindings")
def bindings(target_project: str | None = None, environment: str | None = None) -> dict[str, Any]:
    return vault_deployment_binding_service.list_bindings(target_project=target_project, environment=environment)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return vault_deployment_binding_service.package()
