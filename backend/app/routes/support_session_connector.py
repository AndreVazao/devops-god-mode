from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.support_session_connector_service import support_session_connector_service

router = APIRouter(prefix="/api/support-session", tags=["support-session"])


class CreateSessionPayload(BaseModel):
    ttl_minutes: int = 60
    mode: str = "assisted_action"
    reason: str = "Temporary support/test session for installed God Mode."
    tenant_id: str = "owner-andre"


class DiagnosticsPayload(BaseModel):
    support_session_id: str | None = None


class ProposeActionPayload(BaseModel):
    support_session_id: str
    title: str
    action_type: str
    reason: str
    proposed_payload: dict[str, Any] | None = None
    risk_level: str = "low"
    rollback_hint: str = "No automatic rollback required."
    tenant_id: str = "owner-andre"


class ResultPayload(BaseModel):
    support_action_id: str
    result_summary: str
    status: str = "completed"
    tenant_id: str = "owner-andre"


class RevokePayload(BaseModel):
    support_session_id: str
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return support_session_connector_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return support_session_connector_service.policy()


@router.post("/create")
def create_session(payload: CreateSessionPayload) -> dict[str, Any]:
    return support_session_connector_service.create_session(
        ttl_minutes=payload.ttl_minutes,
        mode=payload.mode,
        reason=payload.reason,
        tenant_id=payload.tenant_id,
    )


@router.post("/diagnostics")
def diagnostics(payload: DiagnosticsPayload) -> dict[str, Any]:
    return support_session_connector_service.redacted_diagnostics(
        support_session_id=payload.support_session_id,
    )


@router.post("/propose-action")
def propose_action(payload: ProposeActionPayload) -> dict[str, Any]:
    return support_session_connector_service.propose_action(
        support_session_id=payload.support_session_id,
        title=payload.title,
        action_type=payload.action_type,
        reason=payload.reason,
        proposed_payload=payload.proposed_payload,
        risk_level=payload.risk_level,
        rollback_hint=payload.rollback_hint,
        tenant_id=payload.tenant_id,
    )


@router.post("/record-action-result")
def record_action_result(payload: ResultPayload) -> dict[str, Any]:
    return support_session_connector_service.record_action_result(
        support_action_id=payload.support_action_id,
        result_summary=payload.result_summary,
        status=payload.status,
        tenant_id=payload.tenant_id,
    )


@router.post("/revoke")
def revoke_session(payload: RevokePayload) -> dict[str, Any]:
    return support_session_connector_service.revoke_session(
        support_session_id=payload.support_session_id,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return support_session_connector_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return support_session_connector_service.package()
