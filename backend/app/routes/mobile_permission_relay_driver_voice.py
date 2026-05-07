from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.god_mode_local_vault_service import god_mode_local_vault_service
from app.services.mobile_permission_popup_contract_service import mobile_permission_popup_contract_service
from app.services.mobile_permission_relay_driver_voice_service import mobile_permission_relay_driver_voice_service

router = APIRouter(prefix="/api/mobile-permission-relay", tags=["mobile-permission-relay"])


class PermissionRequestPayload(BaseModel):
    title: str
    body: str
    request_type: str = "approval"
    project_id: str = "GOD_MODE"
    source_ref: dict[str, Any] | None = None
    priority: str = "medium"
    requires_sensitive_input: bool = False
    form_schema: list[dict[str, Any]] | None = None
    wait_for_response: bool = True
    ttl_minutes: int = 60
    tenant_id: str = "owner-andre"


class RequestIdPayload(BaseModel):
    permission_request_id: str
    tenant_id: str = "owner-andre"


class OfflinePayload(BaseModel):
    permission_request_id: str
    reason: str = "phone_offline_or_no_network"
    tenant_id: str = "owner-andre"


class DeliveryPayload(BaseModel):
    permission_request_id: str
    delivery_channel: str = "mobile_cockpit"
    device_hint: str = "android_phone"
    tenant_id: str = "owner-andre"


class DecisionPayload(BaseModel):
    permission_request_id: str
    decision: str
    operator_note: str = ""
    form_values: dict[str, Any] | None = None
    via: str = "mobile_popup"
    tenant_id: str = "owner-andre"


class VoicePayload(BaseModel):
    transcript: str
    intent: str = "unknown"
    permission_request_id: str | None = None
    driving_mode: bool = True
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.policy()


@router.post("/create-request")
def create_request(payload: PermissionRequestPayload) -> dict[str, Any]:
    result = mobile_permission_relay_driver_voice_service.create_permission_request(
        title=payload.title,
        body=payload.body,
        request_type=payload.request_type,
        project_id=payload.project_id,
        source_ref=payload.source_ref,
        priority=payload.priority,
        requires_sensitive_input=payload.requires_sensitive_input,
        form_schema=payload.form_schema,
        wait_for_response=payload.wait_for_response,
        ttl_minutes=payload.ttl_minutes,
        tenant_id=payload.tenant_id,
    )
    if result.get("permission_request"):
        result["popup_contract"] = mobile_permission_popup_contract_service.build_contract(
            permission_request=result["permission_request"],
        )
    return result


@router.get("/popup-contract-examples")
@router.post("/popup-contract-examples")
def popup_contract_examples() -> dict[str, Any]:
    return mobile_permission_popup_contract_service.example_contracts()


@router.post("/mark-sent")
def mark_sent(payload: DeliveryPayload) -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.mark_sent(
        permission_request_id=payload.permission_request_id,
        delivery_channel=payload.delivery_channel,
        device_hint=payload.device_hint,
        tenant_id=payload.tenant_id,
    )


@router.post("/mark-delivered")
def mark_delivered(payload: DeliveryPayload) -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.mark_delivered(
        permission_request_id=payload.permission_request_id,
        delivery_channel=payload.delivery_channel,
        device_hint=payload.device_hint,
        tenant_id=payload.tenant_id,
    )


@router.post("/mark-offline-wait")
def mark_offline_wait(payload: OfflinePayload) -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.mark_offline_wait(
        permission_request_id=payload.permission_request_id,
        reason=payload.reason,
        tenant_id=payload.tenant_id,
    )


@router.post("/mark-resend-pending")
def mark_resend_pending(payload: OfflinePayload) -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.mark_resend_pending(
        permission_request_id=payload.permission_request_id,
        reason=payload.reason,
        tenant_id=payload.tenant_id,
    )


@router.post("/decide")
def decide(payload: DecisionPayload) -> dict[str, Any]:
    result = mobile_permission_relay_driver_voice_service.decide_permission(
        permission_request_id=payload.permission_request_id,
        decision=payload.decision,
        operator_note=payload.operator_note,
        form_values=payload.form_values,
        via=payload.via,
        tenant_id=payload.tenant_id,
    )
    request = result.get("permission_request") or {}
    normalized = str(payload.decision).lower().strip()
    approved = normalized in {"approved", "approve", "ok", "sim", "yes"} or request.get("status") == "approved"
    if approved and payload.form_values and request.get("requires_sensitive_input"):
        vault_refs = []
        schema = request.get("form_schema", []) or []
        sensitive_fields = {str(field.get("name")): field for field in schema if field.get("sensitive")}
        for field_name, field in sensitive_fields.items():
            raw_value = payload.form_values.get(field_name)
            if raw_value:
                source_ref = request.get("source_ref") or {}
                provider = str(source_ref.get("provider") or source_ref.get("type") or request.get("request_type") or "manual")
                stored = god_mode_local_vault_service.store_secret(
                    raw_secret=str(raw_value),
                    label=f"{provider}:{request.get('project_id', 'GOD_MODE')}:{field_name}",
                    purpose=f"{request.get('title', 'Permission request')} | {request.get('body', '')[:180]}",
                    secret_kind=str(field.get("type") or "credential"),
                    provider=provider,
                    project_id=str(request.get("project_id") or "GOD_MODE"),
                    scope="project",
                    source_ref={"type": "mobile_permission_relay", "permission_request_id": payload.permission_request_id, "field": field_name, **source_ref},
                    reuse_policy="reuse_for_same_provider_project_and_purpose",
                    tenant_id=payload.tenant_id,
                )
                if stored.get("vault_reference"):
                    vault_refs.append(stored["vault_reference"])
        result["vault_references_created"] = vault_refs
        result["sensitive_values_stored_in_vault"] = bool(vault_refs)
        result["raw_secret_values_returned"] = False
    return result


@router.post("/voice-event")
def voice_event(payload: VoicePayload) -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.register_voice_event(
        transcript=payload.transcript,
        intent=payload.intent,
        permission_request_id=payload.permission_request_id,
        driving_mode=payload.driving_mode,
        tenant_id=payload.tenant_id,
    )


@router.get("/poll")
def poll(tenant_id: str = "owner-andre", limit: int = 50) -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.poll_pending_for_mobile(tenant_id=tenant_id, limit=limit)


@router.get("/wait-status/{permission_request_id}")
def wait_status(permission_request_id: str) -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.wait_status(permission_request_id=permission_request_id)


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard(tenant_id: str = "owner-andre") -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.dashboard(tenant_id=tenant_id)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return mobile_permission_relay_driver_voice_service.package()
