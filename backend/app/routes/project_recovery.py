from fastapi import APIRouter, HTTPException

from app.services.project_recovery_service import project_recovery_service

router = APIRouter(prefix="/api/project-recovery", tags=["project-recovery"])


@router.get("/status")
async def project_recovery_status():
    projects = project_recovery_service.get_projects()["projects"]
    return {
        "ok": True,
        "mode": "project_recovery_status",
        "projects_count": len(projects),
        "recovery_status": "project_recovery_ready",
    }


@router.get("/projects")
async def project_recovery_projects():
    return project_recovery_service.get_projects()


@router.get("/sources")
async def project_recovery_sources(recovery_project_id: str | None = None):
    return project_recovery_service.get_sources(recovery_project_id)


@router.get("/scripts")
async def project_recovery_scripts(recovery_project_id: str | None = None):
    return project_recovery_service.get_scripts(recovery_project_id)


@router.get("/blueprint/{recovery_project_id}")
async def project_recovery_blueprint(recovery_project_id: str):
    try:
        return project_recovery_service.get_repo_blueprint(recovery_project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-recovery")
async def project_recovery_next_recovery():
    return project_recovery_service.get_next_recovery()
