from fastapi import APIRouter

from app.services.pc_first_core_extraction_service import (
    pc_first_core_extraction_service,
)

router = APIRouter(
    prefix="/api/pc-first-core-extraction",
    tags=["pc-first-core-extraction"],
)


@router.get("/status")
async def pc_first_core_extraction_status():
    surfaces = pc_first_core_extraction_service.get_core_surfaces()["surfaces"]
    return {
        "ok": True,
        "mode": "pc_first_core_extraction_status",
        "surfaces_count": len(surfaces),
        "pc_first_status": "pc_first_core_extraction_ready",
    }


@router.get("/surfaces")
async def pc_first_core_surfaces():
    return pc_first_core_extraction_service.get_core_surfaces()


@router.get("/actions")
async def pc_first_extraction_actions(extraction_area: str | None = None):
    return pc_first_core_extraction_service.get_extraction_actions(extraction_area)


@router.get("/package")
async def pc_first_extraction_package():
    return pc_first_core_extraction_service.get_extraction_package()


@router.get("/next-extraction-action")
async def next_pc_first_extraction_action():
    return pc_first_core_extraction_service.get_next_extraction_action()
