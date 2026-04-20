from fastapi import APIRouter, HTTPException

from app.services.project_recovery_real_write_link_service import (
    project_recovery_real_write_link_service,
)

router = APIRouter(prefix="/api/project-recovery-real-write", tags=["project-recovery-real-write"])


@router.get("/status")
async def project_recovery_real_write_status():
    handoffs = project_recovery_real_write_link_service.get_handoffs()["handoffs"]
    return {
        "ok": True,
        "mode": "project_recovery_real_write_status",
        "handoffs_count": len(handoffs),
        "real_write_handoff_status": "project_recovery_real_write_ready",
    }


@router.get("/handoffs")
async def project_recovery_real_write_handoffs():
    return project_recovery_real_write_link_service.get_handoffs()


@router.get("/targets")
async def project_recovery_real_write_targets(recovery_project_id: str | None = None):
    return project_recovery_real_write_link_service.get_handoff_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_real_write_package(recovery_project_id: str):
    try:
        return project_recovery_real_write_link_service.get_real_write_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-handoff-action")
async def project_recovery_real_write_next_handoff_action():
    return project_recovery_real_write_link_service.get_next_handoff_action()
