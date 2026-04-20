from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_create_service import (
    project_recovery_write_create_service,
)

router = APIRouter(prefix="/api/project-recovery-write-create", tags=["project-recovery-write-create"])


@router.get("/status")
async def project_recovery_write_create_status():
    requests = project_recovery_write_create_service.get_create_requests()["requests"]
    return {
        "ok": True,
        "mode": "project_recovery_write_create_status",
        "requests_count": len(requests),
        "create_status": "project_recovery_write_create_ready",
    }


@router.get("/requests")
async def project_recovery_write_create_requests():
    return project_recovery_write_create_service.get_create_requests()


@router.get("/targets")
async def project_recovery_write_create_targets(recovery_project_id: str | None = None):
    return project_recovery_write_create_service.get_create_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_create_package(recovery_project_id: str):
    try:
        return project_recovery_write_create_service.get_create_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-create-action")
async def project_recovery_write_create_next_action():
    return project_recovery_write_create_service.get_next_create_action()
