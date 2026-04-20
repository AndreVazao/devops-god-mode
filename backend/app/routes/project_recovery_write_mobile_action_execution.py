from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_mobile_action_execution_service import (
    project_recovery_write_mobile_action_execution_service,
)

router = APIRouter(
    prefix="/api/project-recovery-write-mobile-action-execution",
    tags=["project-recovery-write-mobile-action-execution"],
)


@router.get("/status")
async def project_recovery_write_mobile_action_execution_status():
    executions = project_recovery_write_mobile_action_execution_service.get_mobile_executions()["executions"]
    return {
        "ok": True,
        "mode": "project_recovery_write_mobile_action_execution_status",
        "executions_count": len(executions),
        "mobile_execution_status": "project_recovery_write_mobile_action_execution_ready",
    }


@router.get("/executions")
async def project_recovery_write_mobile_executions():
    return project_recovery_write_mobile_action_execution_service.get_mobile_executions()


@router.get("/effects")
async def project_recovery_write_mobile_effects(recovery_project_id: str | None = None):
    return project_recovery_write_mobile_action_execution_service.get_mobile_effects(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_mobile_execution_package(recovery_project_id: str):
    try:
        return project_recovery_write_mobile_action_execution_service.get_mobile_execution_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-mobile-execution")
async def project_recovery_write_next_mobile_execution():
    return project_recovery_write_mobile_action_execution_service.get_next_mobile_execution()
