from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_approval_cockpit_service import (
    project_recovery_write_approval_cockpit_service,
)

router = APIRouter(
    prefix="/api/project-recovery-write-approval-cockpit",
    tags=["project-recovery-write-approval-cockpit"],
)


@router.get("/status")
async def project_recovery_write_approval_cockpit_status():
    cockpits = project_recovery_write_approval_cockpit_service.get_cockpits()["cockpits"]
    return {
        "ok": True,
        "mode": "project_recovery_write_approval_cockpit_status",
        "cockpits_count": len(cockpits),
        "cockpit_status": "project_recovery_write_approval_cockpit_ready",
    }


@router.get("/cockpits")
async def project_recovery_write_approval_cockpits():
    return project_recovery_write_approval_cockpit_service.get_cockpits()


@router.get("/items")
async def project_recovery_write_approval_items(recovery_project_id: str | None = None):
    return project_recovery_write_approval_cockpit_service.get_approval_items(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_approval_package(recovery_project_id: str):
    try:
        return project_recovery_write_approval_cockpit_service.get_cockpit_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-approval-action")
async def project_recovery_write_next_approval_action():
    return project_recovery_write_approval_cockpit_service.get_next_approval_action()
