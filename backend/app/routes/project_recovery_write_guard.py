from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_guard_service import (
    project_recovery_write_guard_service,
)

router = APIRouter(prefix="/api/project-recovery-write-guard", tags=["project-recovery-write-guard"])


@router.get("/status")
async def project_recovery_write_guard_status():
    guards = project_recovery_write_guard_service.get_guards()["guards"]
    return {
        "ok": True,
        "mode": "project_recovery_write_guard_status",
        "guards_count": len(guards),
        "guard_status": "project_recovery_write_guard_ready",
    }


@router.get("/guards")
async def project_recovery_write_guards():
    return project_recovery_write_guard_service.get_guards()


@router.get("/findings")
async def project_recovery_write_guard_findings(recovery_project_id: str | None = None):
    return project_recovery_write_guard_service.get_findings(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_guard_package(recovery_project_id: str):
    try:
        return project_recovery_write_guard_service.get_guard_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-guard-action")
async def project_recovery_write_guard_next_action():
    return project_recovery_write_guard_service.get_next_guard_action()
