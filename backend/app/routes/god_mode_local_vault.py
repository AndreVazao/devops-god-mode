from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.god_mode_local_vault_service import god_mode_local_vault_service
from app.services.god_mode_secret_intake_classifier_service import god_mode_secret_intake_classifier_service

router = APIRouter(prefix="/api/god-mode-vault", tags=["god-mode-vault"])


class StoreSecretPayload(BaseModel):
    raw_secret: str
    label: str
    purpose: str
    secret_kind: str = "credential"
    provider: str = "manual"
    project_id: str = "GOD_MODE"
    scope: str = "project"
    source_ref: dict[str, Any] | None = None
    reuse_policy: str = "reuse_for_same_provider_project_and_purpose"
    tenant_id: str = "owner-andre"


class IntakeTextPayload(BaseModel):
    text: str
    project_hint: str = "GOD_MODE"
    default_provider: str = "auto"
    source: str = "mobile_popup_or_operator_paste"
    tenant_id: str = "owner-andre"
    store_real_values: bool = True


class TokenPlanPayload(BaseModel):
    provider: str
    purpose: str
    project_id: str = "GOD_MODE"
    required_scopes: list[str] | None = None
    tenant_id: str = "owner-andre"


class RevealPayload(BaseModel):
    vault_item_id: str
    approved_gate_id: str | None = None
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return god_mode_local_vault_service.status()


@router.post("/store-secret")
def store_secret(payload: StoreSecretPayload) -> dict[str, Any]:
    return god_mode_local_vault_service.store_secret(
        raw_secret=payload.raw_secret,
        label=payload.label,
        purpose=payload.purpose,
        secret_kind=payload.secret_kind,
        provider=payload.provider,
        project_id=payload.project_id,
        scope=payload.scope,
        source_ref=payload.source_ref,
        reuse_policy=payload.reuse_policy,
        tenant_id=payload.tenant_id,
    )


@router.post("/intake-text")
def intake_text(payload: IntakeTextPayload) -> dict[str, Any]:
    return god_mode_secret_intake_classifier_service.ingest_text(
        text=payload.text,
        project_hint=payload.project_hint,
        default_provider=payload.default_provider,
        source=payload.source,
        tenant_id=payload.tenant_id,
        store_real_values=payload.store_real_values,
    )


@router.post("/plan-needed-token")
def plan_needed_token(payload: TokenPlanPayload) -> dict[str, Any]:
    return god_mode_secret_intake_classifier_service.plan_needed_token(
        provider=payload.provider,
        purpose=payload.purpose,
        project_id=payload.project_id,
        required_scopes=payload.required_scopes,
        tenant_id=payload.tenant_id,
    )


@router.get("/references")
def references(provider: str | None = None, project_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    return god_mode_local_vault_service.list_references(provider=provider, project_id=project_id, limit=limit)


@router.post("/reveal-for-runtime")
def reveal_for_runtime(payload: RevealPayload) -> dict[str, Any]:
    return god_mode_local_vault_service.reveal_for_runtime(
        vault_item_id=payload.vault_item_id,
        approved_gate_id=payload.approved_gate_id,
        tenant_id=payload.tenant_id,
    )


@router.get("/intake-status")
@router.post("/intake-status")
def intake_status() -> dict[str, Any]:
    return god_mode_secret_intake_classifier_service.status()
