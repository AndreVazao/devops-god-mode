from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_submit_service import (
    project_recovery_write_submit_service,
)

router = APIRouter(prefix="/api/project-recovery-write-submit", tags=["project-recovery-write-submit"])


@router.get("/status")
async def project_recovery_write_submit_status():
    submissions = project_recovery_write_submit_service.get_submissions()["submissions"]
    return {
        "ok": True,
        "mode": "project_recovery_write_submit_status",
        "submissions_count": len(submissions),
        "submit_status": "project_recovery_write_submit_ready",
    }


@router.get("/submissions")
async def project_recovery_write_submissions():
    return project_recovery_write_submit_service.get_submissions()


@router.get("/targets")
async def project_recovery_write_submit_targets(recovery_project_id: str | None = None):
    return project_recovery_write_submit_service.get_submit_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_submit_package(recovery_project_id: str):
    try:
        return project_recovery_write_submit_service.get_submit_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-submit-action")
async def project_recovery_write_submit_next_action():
    return project_recovery_write_submit_service.get_next_submit_action()
