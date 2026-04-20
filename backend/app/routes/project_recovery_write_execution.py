from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_execution_service import (
    project_recovery_write_execution_service,
)

router = APIRouter(
    prefix="/api/project-recovery-write-execution",
    tags=["project-recovery-write-execution"],
)


@router.get("/status")
async def project_recovery_write_execution_status():
    sessions = project_recovery_write_execution_service.get_execution_sessions()["sessions"]
    return {
        "ok": True,
        "mode": "project_recovery_write_execution_status",
        "sessions_count": len(sessions),
        "execution_status": "project_recovery_write_execution_ready",
    }


@router.get("/sessions")
async def project_recovery_write_execution_sessions():
    return project_recovery_write_execution_service.get_execution_sessions()


@router.get("/results")
async def project_recovery_write_execution_results(recovery_project_id: str | None = None):
    return project_recovery_write_execution_service.get_execution_results(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_execution_package(recovery_project_id: str):
    try:
        return project_recovery_write_execution_service.get_execution_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-execution-action")
async def project_recovery_write_execution_next_action():
    return project_recovery_write_execution_service.get_next_execution_action()
