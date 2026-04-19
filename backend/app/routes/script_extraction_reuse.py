from fastapi import APIRouter

from app.services.script_extraction_reuse_service import script_extraction_reuse_service

router = APIRouter(prefix="/api/script-reuse", tags=["script-reuse"])


@router.get("/status")
async def script_reuse_status():
    scripts = script_extraction_reuse_service.get_extracted_scripts()["scripts"]
    return {
        "ok": True,
        "mode": "script_reuse_status",
        "scripts_count": len(scripts),
        "reuse_status": "script_reuse_ready",
    }


@router.get("/scripts")
async def script_reuse_scripts():
    return script_extraction_reuse_service.get_extracted_scripts()


@router.get("/projects")
async def script_reuse_projects():
    return script_extraction_reuse_service.get_scripts_by_project()


@router.get("/maps")
async def script_reuse_maps():
    return script_extraction_reuse_service.get_reuse_maps()


@router.get("/best-candidates")
async def script_reuse_best_candidates():
    return script_extraction_reuse_service.get_best_candidates()
