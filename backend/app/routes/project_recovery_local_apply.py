from fastapi import APIRouter, HTTPException

from app.services.project_recovery_local_apply_service import (
    project_recovery_local_apply_service,
)

router = APIRouter(prefix="/api/project-recovery-local-apply", tags=["project-recovery-local-apply"])


@router.get("/status")
async def project_recovery_local_apply_status():
    bundles = project_recovery_local_apply_service.get_local_apply_bundles()["bundles"]
    return {
        "ok": True,
        "mode": "project_recovery_local_apply_status",
        "bundles_count": len(bundles),
        "local_apply_status": "project_recovery_local_apply_ready",
    }


@router.get("/bundles")
async def project_recovery_local_apply_bundles():
    return project_recovery_local_apply_service.get_local_apply_bundles()


@router.get("/targets")
async def project_recovery_local_apply_targets(recovery_project_id: str | None = None):
    return project_recovery_local_apply_service.get_local_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_local_apply_package(recovery_project_id: str):
    try:
        return project_recovery_local_apply_service.get_local_apply_package(recovery_project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/write-ready/{recovery_project_id}")
async def project_recovery_local_apply_write_ready(recovery_project_id: str):
    try:
        return project_recovery_local_apply_service.get_write_ready_package(recovery_project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-local-action")
async def project_recovery_local_apply_next_local_action():
    return project_recovery_local_apply_service.get_next_local_action()


@router.get("/next-write-ready-action")
async def project_recovery_local_apply_next_write_ready_action():
    return project_recovery_local_apply_service.get_next_write_ready_action()
