from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_candidate_service import (
    project_recovery_write_candidate_service,
)

router = APIRouter(prefix="/api/project-recovery-write-candidates", tags=["project-recovery-write-candidates"])


@router.get("/status")
async def project_recovery_write_candidates_status():
    candidates = project_recovery_write_candidate_service.get_candidates()["candidates"]
    return {
        "ok": True,
        "mode": "project_recovery_write_candidates_status",
        "candidates_count": len(candidates),
        "candidate_status": "project_recovery_write_candidates_ready",
    }


@router.get("/candidates")
async def project_recovery_write_candidates():
    return project_recovery_write_candidate_service.get_candidates()


@router.get("/targets")
async def project_recovery_write_candidate_targets(recovery_project_id: str | None = None):
    return project_recovery_write_candidate_service.get_candidate_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_candidate_package(recovery_project_id: str):
    try:
        return project_recovery_write_candidate_service.get_candidate_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-candidate-action")
async def project_recovery_write_candidate_next_action():
    return project_recovery_write_candidate_service.get_next_candidate_action()
