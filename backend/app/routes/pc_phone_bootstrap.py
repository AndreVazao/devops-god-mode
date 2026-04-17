from fastapi import APIRouter, HTTPException

from app.services.pc_phone_bootstrap_service import pc_phone_bootstrap_service

router = APIRouter(prefix="/api/pc-phone-bootstrap", tags=["pc-phone-bootstrap"])


@router.get("/status")
async def pc_phone_bootstrap_status():
    data = pc_phone_bootstrap_service.get_bootstrap_foundation()
    return {
        "ok": True,
        "mode": data["mode"],
        "bootstrap_profiles_count": len(data["bootstrap_profiles"]),
        "updated_at": data["updated_at"],
    }


@router.get("/profiles")
async def pc_phone_bootstrap_profiles():
    return {
        "ok": True,
        "bootstrap_profiles": pc_phone_bootstrap_service.list_bootstrap_profiles(),
    }


@router.get("/pairing-payload")
async def pc_phone_pairing_payload():
    try:
        return pc_phone_bootstrap_service.generate_pairing_payload()
    except ValueError:
        raise HTTPException(status_code=404, detail="bootstrap_profile_not_found")


@router.post("/promote")
async def pc_phone_bootstrap_promote():
    try:
        return pc_phone_bootstrap_service.promote_runtime_mode()
    except ValueError:
        raise HTTPException(status_code=404, detail="bootstrap_profile_not_found")
