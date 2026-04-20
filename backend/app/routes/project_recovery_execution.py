from fastapi import APIRouter, HTTPException

from app.services.project_recovery_execution_service import (
    project_recovery_execution_service,
)

router = APIRouter(prefix="/api/project-recovery-execution", tags=["project-recovery-execution"])


@router.get("/status")
async def project_recovery_execution_status():
    bundles = project_recovery_execution_service.get_execution_bundles()["bundles"]
    return {
        "ok": True,
        "mode": "project_recovery_execution_status",
        "bundles_count": len(bundles),
        "execution_status": "project_recovery_execution_ready",
    }


@router.get("/bundles")
async def project_recovery_execution_bundles():
    return project_recovery_execution_service.get_execution_bundles()


@router.get("/target-files")
async def project_recovery_execution_target_files(recovery_project_id: str | None = None):
    return project_recovery_execution_service.get_target_files(recovery_project_id)


@router.get("/materialization-plan/{recovery_project_id}")
async def project_recovery_execution_materialization_plan(recovery_project_id: str):
    try:
        return project_recovery_execution_service.get_materialization_plan(recovery_project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-execution")
async def project_recovery_execution_next_execution():
    return project_recovery_execution_service.get_next_execution()
