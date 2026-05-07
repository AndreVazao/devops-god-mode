from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ia_operator_permission_vault_bridge_service import ia_operator_permission_vault_bridge_service

router = APIRouter(prefix="/api/ia-operator-bridge", tags=["ia-operator-bridge"])


class StartLoopPayload(BaseModel):
    goal: str = "Make God Mode installable, usable and self-improving on the home PC."
    project_id: str = "GOD_MODE"
    providers: list[str] | None = None
    tenant_id: str = "owner-andre"


class BindPacketPayload(BaseModel):
    work_packet_id: str
    tenant_id: str = "owner-andre"


class ProviderNotePayload(BaseModel):
    work_packet_id: str
    note_text: str
    provider: str = "manual_ai"
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return ia_operator_permission_vault_bridge_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return ia_operator_permission_vault_bridge_service.policy()


@router.post("/start-loop")
def start_loop(payload: StartLoopPayload) -> dict[str, Any]:
    return ia_operator_permission_vault_bridge_service.start_first_autonomous_work_loop(
        goal=payload.goal,
        project_id=payload.project_id,
        providers=payload.providers,
        tenant_id=payload.tenant_id,
    )


@router.post("/bind-packet")
def bind_packet(payload: BindPacketPayload) -> dict[str, Any]:
    return ia_operator_permission_vault_bridge_service.bind_packet_to_vault_or_permission(
        work_packet_id=payload.work_packet_id,
        tenant_id=payload.tenant_id,
    )


@router.post("/continue-with-note")
def continue_with_note(payload: ProviderNotePayload) -> dict[str, Any]:
    return ia_operator_permission_vault_bridge_service.ingest_provider_response_and_continue(
        work_packet_id=payload.work_packet_id,
        response_text=payload.note_text,
        provider=payload.provider,
        tenant_id=payload.tenant_id,
    )


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return ia_operator_permission_vault_bridge_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return ia_operator_permission_vault_bridge_service.package()
