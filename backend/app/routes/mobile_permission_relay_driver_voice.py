from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

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
    return mobile_permission_relay_driver_voice_service.create_permission_request(
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
    return mobile_permission_relay_driver_voice_service.decide_permission(
        permission_request_id=payload.permission_request_id,
        decision=payload.decision,
        operator_note=payload.operator_note,
        form_values=payload.form_values,
        via=payload.via,
        tenant_id=payload.tenant_id,
    )


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
