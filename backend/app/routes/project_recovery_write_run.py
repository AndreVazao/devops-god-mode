from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_run_service import (
    project_recovery_write_run_service,
)

router = APIRouter(prefix="/api/project-recovery-write-runs", tags=["project-recovery-write-runs"])


@router.get("/status")
async def project_recovery_write_runs_status():
    runs = project_recovery_write_run_service.get_runs()["runs"]
    return {
        "ok": True,
        "mode": "project_recovery_write_runs_status",
        "runs_count": len(runs),
        "run_status": "project_recovery_write_runs_ready",
    }


@router.get("/runs")
async def project_recovery_write_runs():
    return project_recovery_write_run_service.get_runs()


@router.get("/targets")
async def project_recovery_write_run_targets(recovery_project_id: str | None = None):
    return project_recovery_write_run_service.get_run_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_run_package(recovery_project_id: str):
    try:
        return project_recovery_write_run_service.get_run_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-run-action")
async def project_recovery_write_run_next_action():
    return project_recovery_write_run_service.get_next_run_action()
