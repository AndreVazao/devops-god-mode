from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.lab_best_of_work_ally_service import lab_best_of_work_ally_service

router = APIRouter(prefix="/api/lab-best-of-work-ally", tags=["lab-best-of-work-ally"])


class CommandPlanRequest(BaseModel):
    command: str = "Avança"


@router.get("/status")
@router.post("/status")
def status() -> dict[str, Any]:
    return lab_best_of_work_ally_service.status()


@router.get("/patterns")
@router.post("/patterns")
def patterns() -> dict[str, Any]:
    return lab_best_of_work_ally_service.best_patterns()


@router.get("/rules")
@router.post("/rules")
def rules() -> dict[str, Any]:
    return lab_best_of_work_ally_service.work_ally_operating_rules()


@router.post("/command-plan")
def command_plan(payload: CommandPlanRequest) -> dict[str, Any]:
    return lab_best_of_work_ally_service.command_to_work_plan(payload.command)


@router.get("/workflow-hygiene")
@router.post("/workflow-hygiene")
def workflow_hygiene() -> dict[str, Any]:
    return lab_best_of_work_ally_service.workflow_hygiene_policy()


@router.get("/source-labs")
@router.post("/source-labs")
def source_labs() -> dict[str, Any]:
    return lab_best_of_work_ally_service.source_lab_snapshot()


@router.get("/package")
@router.post("/package")
def package() -> dict[str, Any]:
    return lab_best_of_work_ally_service.package()
