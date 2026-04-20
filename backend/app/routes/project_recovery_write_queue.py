from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_queue_service import (
    project_recovery_write_queue_service,
)

router = APIRouter(prefix="/api/project-recovery-write-queue", tags=["project-recovery-write-queue"])


@router.get("/status")
async def project_recovery_write_queue_status():
    entries = project_recovery_write_queue_service.get_queue_entries()["entries"]
    return {
        "ok": True,
        "mode": "project_recovery_write_queue_status",
        "entries_count": len(entries),
        "queue_status": "project_recovery_write_queue_ready",
    }


@router.get("/entries")
async def project_recovery_write_queue_entries():
    return project_recovery_write_queue_service.get_queue_entries()


@router.get("/targets")
async def project_recovery_write_queue_targets(recovery_project_id: str | None = None):
    return project_recovery_write_queue_service.get_queue_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_queue_package(recovery_project_id: str):
    try:
        return project_recovery_write_queue_service.get_queue_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-queue-action")
async def project_recovery_write_queue_next_action():
    return project_recovery_write_queue_service.get_next_queue_action()
