from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_dispatch_service import (
    project_recovery_write_dispatch_service,
)

router = APIRouter(prefix="/api/project-recovery-write-dispatch", tags=["project-recovery-write-dispatch"])


@router.get("/status")
async def project_recovery_write_dispatch_status():
    dispatches = project_recovery_write_dispatch_service.get_dispatches()["dispatches"]
    return {
        "ok": True,
        "mode": "project_recovery_write_dispatch_status",
        "dispatches_count": len(dispatches),
        "dispatch_status": "project_recovery_write_dispatch_ready",
    }


@router.get("/dispatches")
async def project_recovery_write_dispatches():
    return project_recovery_write_dispatch_service.get_dispatches()


@router.get("/targets")
async def project_recovery_write_dispatch_targets(recovery_project_id: str | None = None):
    return project_recovery_write_dispatch_service.get_dispatch_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_dispatch_package(recovery_project_id: str):
    try:
        return project_recovery_write_dispatch_service.get_dispatch_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-dispatch-action")
async def project_recovery_write_dispatch_next_action():
    return project_recovery_write_dispatch_service.get_next_dispatch_action()
