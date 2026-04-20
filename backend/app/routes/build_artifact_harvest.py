from fastapi import APIRouter, HTTPException

from app.services.build_artifact_harvest_service import (
    build_artifact_harvest_service,
)

router = APIRouter(
    prefix="/api/build-artifact-harvest",
    tags=["build-artifact-harvest"],
)


@router.get("/status")
async def build_artifact_harvest_status():
    harvests = build_artifact_harvest_service.get_harvests()["harvests"]
    return {
        "ok": True,
        "mode": "build_artifact_harvest_status",
        "harvests_count": len(harvests),
        "harvest_status": "build_artifact_harvest_ready",
    }


@router.get("/harvests")
async def build_artifact_harvests():
    return build_artifact_harvest_service.get_harvests()


@router.get("/items")
async def build_artifact_items(recovery_project_id: str | None = None):
    return build_artifact_harvest_service.get_artifact_items(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def build_artifact_harvest_package(recovery_project_id: str):
    try:
        return build_artifact_harvest_service.get_harvest_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-harvest-action")
async def build_artifact_next_harvest_action():
    return build_artifact_harvest_service.get_next_harvest_action()
