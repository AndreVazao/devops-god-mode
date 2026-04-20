from fastapi import APIRouter, HTTPException

from app.services.project_recovery_write_materialize_service import (
    project_recovery_write_materialize_service,
)

router = APIRouter(
    prefix="/api/project-recovery-write-materialize",
    tags=["project-recovery-write-materialize"],
)


@router.get("/status")
async def project_recovery_write_materialize_status():
    bridges = project_recovery_write_materialize_service.get_materialize_bridges()["bridges"]
    return {
        "ok": True,
        "mode": "project_recovery_write_materialize_status",
        "bridges_count": len(bridges),
        "bridge_status": "project_recovery_write_materialize_ready",
    }


@router.get("/bridges")
async def project_recovery_write_materialize_bridges():
    return project_recovery_write_materialize_service.get_materialize_bridges()


@router.get("/targets")
async def project_recovery_write_materialize_targets(recovery_project_id: str | None = None):
    return project_recovery_write_materialize_service.get_materialize_targets(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def project_recovery_write_materialize_package(recovery_project_id: str):
    try:
        return project_recovery_write_materialize_service.get_materialize_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-materialize-action")
async def project_recovery_write_materialize_next_action():
    return project_recovery_write_materialize_service.get_next_materialize_action()
