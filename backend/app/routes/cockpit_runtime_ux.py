from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.cockpit_runtime_ux_service import cockpit_runtime_ux_service

router = APIRouter(prefix="/api/cockpit-runtime-ux", tags=["cockpit-runtime-ux"])


class ButtonEventRequest(BaseModel):
    button_id: str
    label: str
    endpoint: str
    method: str = "GET"
    risk: str = "safe"
    phase: str = "clicked"
    outcome: str = "recorded"
    tenant_id: str = "owner-andre"
    module_id: str | None = None
    status_code: int | None = None
    ok: bool | None = None
    error: str | None = None


@router.get("/status")
@router.post("/status")
def status(tenant_id: str = "owner-andre") -> dict[str, Any]:
    return cockpit_runtime_ux_service.status(tenant_id=tenant_id)


@router.get("/package")
@router.post("/package")
def package(tenant_id: str = "owner-andre", history_limit: int = 25) -> dict[str, Any]:
    return cockpit_runtime_ux_service.package(tenant_id=tenant_id, history_limit=history_limit)


@router.get("/history")
@router.post("/history")
def history(tenant_id: str = "owner-andre", limit: int = 25) -> dict[str, Any]:
    return cockpit_runtime_ux_service.history(tenant_id=tenant_id, limit=limit)


@router.get("/quick-history-cards")
@router.post("/quick-history-cards")
def quick_history_cards(tenant_id: str = "owner-andre", limit: int = 10) -> dict[str, Any]:
    return cockpit_runtime_ux_service.quick_history_cards(tenant_id=tenant_id, limit=limit)


@router.post("/log-button-event")
def log_button_event(payload: ButtonEventRequest) -> dict[str, Any]:
    return cockpit_runtime_ux_service.log_button_event(
        button_id=payload.button_id,
        label=payload.label,
        endpoint=payload.endpoint,
        method=payload.method,
        risk=payload.risk,
        phase=payload.phase,
        outcome=payload.outcome,
        tenant_id=payload.tenant_id,
        module_id=payload.module_id,
        status_code=payload.status_code,
        ok=payload.ok,
        error=payload.error,
    )
