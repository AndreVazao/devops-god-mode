from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.first_pc_autopilot_ready_flow_service import first_pc_autopilot_ready_flow_service

router = APIRouter(prefix="/api/first-pc-autopilot-ready", tags=["first-pc-autopilot-ready"])


class StartPayload(BaseModel):
    tenant_id: str = "owner-andre"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return first_pc_autopilot_ready_flow_service.status()


@router.get("/readiness")
@router.post("/readiness")
def readiness() -> dict[str, Any]:
    return first_pc_autopilot_ready_flow_service.readiness_checks()


@router.get("/operator-steps")
@router.post("/operator-steps")
def operator_steps() -> dict[str, Any]:
    return first_pc_autopilot_ready_flow_service.operator_steps()


@router.get("/launch-contract")
@router.post("/launch-contract")
def launch_contract() -> dict[str, Any]:
    return first_pc_autopilot_ready_flow_service.launch_contract()


@router.post("/start-today-autopilot")
def start_today_autopilot(payload: StartPayload) -> dict[str, Any]:
    return first_pc_autopilot_ready_flow_service.start_today_autopilot(tenant_id=payload.tenant_id)


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return first_pc_autopilot_ready_flow_service.package()
