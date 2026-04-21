from fastapi import APIRouter, HTTPException

from app.services.platform_control_hardening_service import (
    platform_control_hardening_service,
)

router = APIRouter(
    prefix="/api/platform-control-hardening",
    tags=["platform-control-hardening"],
)


@router.get("/status")
async def platform_control_status():
    surfaces = platform_control_hardening_service.get_control_surfaces()["surfaces"]
    return {
        "ok": True,
        "mode": "platform_control_status",
        "surfaces_count": len(surfaces),
        "platform_control_status": "platform_control_ready",
    }


@router.get("/surfaces")
async def platform_control_surfaces():
    return platform_control_hardening_service.get_control_surfaces()


@router.get("/actions")
async def platform_control_actions(platform_name: str | None = None):
    return platform_control_hardening_service.get_platform_actions(platform_name)


@router.get("/package/{platform_name}")
async def platform_control_package(platform_name: str):
    try:
        return platform_control_hardening_service.get_control_package(platform_name)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="platform_not_found")


@router.get("/next-platform-action")
async def next_platform_action():
    return platform_control_hardening_service.get_next_platform_action()
