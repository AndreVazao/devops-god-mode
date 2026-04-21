from fastapi import APIRouter, HTTPException

from app.services.project_initiation_bootstrap_service import (
    project_initiation_bootstrap_service,
)

router = APIRouter(
    prefix="/api/project-initiation-bootstrap",
    tags=["project-initiation-bootstrap"],
)


@router.get("/status")
async def project_initiation_status():
    initiations = project_initiation_bootstrap_service.get_initiations()["initiations"]
    return {
        "ok": True,
        "mode": "project_initiation_status",
        "initiations_count": len(initiations),
        "initiation_status": "project_initiation_bootstrap_ready",
    }


@router.get("/initiations")
async def project_initiations():
    return project_initiation_bootstrap_service.get_initiations()


@router.get("/steps")
async def project_bootstrap_steps(source_assistant: str | None = None):
    return project_initiation_bootstrap_service.get_bootstrap_steps(source_assistant)


@router.get("/package/{source_assistant}")
async def project_initiation_package(source_assistant: str):
    try:
        return project_initiation_bootstrap_service.get_initiation_package(source_assistant)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="source_assistant_not_found")


@router.get("/next-initiation-action")
async def next_project_initiation_action():
    return project_initiation_bootstrap_service.get_next_initiation_action()
