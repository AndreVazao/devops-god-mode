from fastapi import APIRouter, HTTPException

from app.services.build_catalog_service import build_catalog_service

router = APIRouter(
    prefix="/api/build-catalog",
    tags=["build-catalog"],
)


@router.get("/status")
async def build_catalog_status():
    catalogs = build_catalog_service.get_catalogs()["catalogs"]
    return {
        "ok": True,
        "mode": "build_catalog_status",
        "catalogs_count": len(catalogs),
        "catalog_status": "build_catalog_ready",
    }


@router.get("/catalogs")
async def build_catalogs():
    return build_catalog_service.get_catalogs()


@router.get("/entries")
async def build_output_entries(recovery_project_id: str | None = None):
    return build_catalog_service.get_output_entries(recovery_project_id)


@router.get("/package/{recovery_project_id}")
async def build_catalog_package(recovery_project_id: str):
    try:
        return build_catalog_service.get_catalog_package(recovery_project_id)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="recovery_project_not_found")


@router.get("/next-catalog-action")
async def build_next_catalog_action():
    return build_catalog_service.get_next_catalog_action()
