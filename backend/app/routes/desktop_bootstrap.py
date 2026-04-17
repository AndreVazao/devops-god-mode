from fastapi import APIRouter, HTTPException

from app.services.desktop_bootstrap_service import Desktop_bootstrap_service

router = APIRouter(prefix="/api/desktop-bootstrap", tags=["desktop-bootstrap"])


@router.get("/status")
async def desktop_bootstrap_status():
    data = Desktop_bootstrap_service.get_foundation()
    return {
        "ok": True,
        "mode": data["mode"],
        "desktop_bootstrap_profiles_count": len(data["desktop_bootstrap_profiles"]),
        "updated_at": data["updated_at"],
    }


@router.get("/profiles")
async def desktop_bootstrap_profiles():
    return {
        "ok": True,
        "desktop_bootstrap_profiles": Desktop_bootstrap_service.list_profiles(),
    }


@router.get("/first-run-payload")
async def desktop_first_run_payload():
    try:
        return Desktop_bootstrap_service.generate_first_run_payload()
    except ValueError:
        raise HTTPException(status_code=404, detail="desktop_bootstrap_profile_not_found")


@router.post("/enable-autostart")
async def desktop_enable_autostart():
    try:
        return Desktop_bootstrap_service.set_autostart(True)
    except ValueError:
        raise HTTPException(status_code=404, detail="desktop_bootstrap_profile_not_found")


@router.post("/disable-autostart")
async def desktop_disable_autostart():
    try:
        return Desktop_bootstrap_service.set_autostart(False)
    except ValueError:
        raise HTTPException(status_code=404, detail="desktop_bootstrap_profile_not_found")
