from fastapi import APIRouter

from app.services.packaging_foundation_service import packaging_foundation_service

router = APIRouter(prefix="/api/packaging-foundation", tags=["packaging-foundation"])


@router.get("/status")
async def packaging_foundation_status():
    data = packaging_foundation_service.get_foundation()
    return {
        "ok": True,
        "mode": data["mode"],
        "build_profiles_count": len(data["build_profiles"]),
        "runtime_topologies_count": len(data["runtime_topologies"]),
        "updated_at": data["updated_at"],
    }


@router.get("/build-profiles")
async def packaging_foundation_build_profiles():
    return {
        "ok": True,
        "build_profiles": packaging_foundation_service.list_build_profiles(),
    }


@router.get("/runtime-topologies")
async def packaging_foundation_runtime_topologies():
    return {
        "ok": True,
        "runtime_topologies": packaging_foundation_service.list_runtime_topologies(),
    }


@router.get("/foundation")
async def packaging_foundation_full():
    return packaging_foundation_service.get_foundation()
