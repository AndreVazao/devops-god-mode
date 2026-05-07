from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.autonomous_ia_work_session_operator_service import autonomous_ia_work_session_operator_service

router = APIRouter(prefix="/api/autonomous-ia-work-session", tags=["autonomous-ia-work-session"])


class CreateSessionPayload(BaseModel):
    title: str
    goal: str
    project_id: str = "GOD_MODE"
    operator_mode: str = "oner_busy_safe"
    tenant_id: str = "owner-andre"


class CreatePacketPayload(BaseModel):
    work_session_id: str
    provider: str
    task_title: str
    task_goal: str
    context: str = ""
    expected_output: str = "implementation advice, risks, file plan and validation steps"
    target_project: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


class SelfDiagnosisPacketsPayload(BaseModel):
    work_session_id: str
    providers: list[str] | None = None
    limit: int = 5
    tenant_id: str = "owner-andre"


class PacketStatusPayload(BaseModel):
    work_packet_id: str
    status: str
    note: str = ""
    tenant_id: str = "owner-andre"


class ImportResponsePayload(BaseModel):
    work_packet_id: str
    response_text: str
    provider: str = "manual_ai"
    tenant_id: str = "owner-andre"


class PacketIdPayload(BaseModel):
    work_packet_id: str
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.status()


@router.get("/policy")
@router.post("/policy")
def policy() -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.policy()


@router.post("/create-session")
def create_session(payload: CreateSessionPayload) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.create_session(
        title=payload.title,
        goal=payload.goal,
        project_id=payload.project_id,
        operator_mode=payload.operator_mode,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-work-packet")
def create_work_packet(payload: CreatePacketPayload) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.create_work_packet(
        work_session_id=payload.work_session_id,
        provider=payload.provider,
        task_title=payload.task_title,
        task_goal=payload.task_goal,
        context=payload.context,
        expected_output=payload.expected_output,
        target_project=payload.target_project,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-packets-from-self-diagnosis")
def create_packets_from_self_diagnosis(payload: SelfDiagnosisPacketsPayload) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.create_packets_from_self_diagnosis(
        work_session_id=payload.work_session_id,
        providers=payload.providers,
        limit=payload.limit,
        tenant_id=payload.tenant_id,
    )


@router.post("/mark-packet-status")
def mark_packet_status(payload: PacketStatusPayload) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.mark_packet_status(
        work_packet_id=payload.work_packet_id,
        status=payload.status,
        note=payload.note,
        tenant_id=payload.tenant_id,
    )


@router.post("/import-response")
def import_response(payload: ImportResponsePayload) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.import_response(
        work_packet_id=payload.work_packet_id,
        response_text=payload.response_text,
        provider=payload.provider,
        tenant_id=payload.tenant_id,
    )


@router.post("/convert-response-to-tasks")
def convert_response_to_tasks(payload: PacketIdPayload) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.convert_response_to_tasks(
        work_packet_id=payload.work_packet_id,
        tenant_id=payload.tenant_id,
    )


@router.post("/create-provider-launcher-contract")
def create_provider_launcher_contract(payload: PacketIdPayload) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.create_provider_launcher_contract(
        work_packet_id=payload.work_packet_id,
        tenant_id=payload.tenant_id,
    )


@router.get("/packets")
def packets(status: str | None = None, provider: str | None = None, limit: int = 100) -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.list_packets(status=status, provider=provider, limit=limit)


@router.get("/dashboard")
@router.post("/dashboard")
def dashboard() -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.dashboard()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return autonomous_ia_work_session_operator_service.package()
