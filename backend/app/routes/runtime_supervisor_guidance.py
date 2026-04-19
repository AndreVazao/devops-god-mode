from fastapi import APIRouter

from app.services.runtime_supervisor_guidance_service import (
    runtime_supervisor_guidance_service,
)

router = APIRouter(prefix="/api/runtime-supervisor", tags=["runtime-supervisor"])


@router.get("/status")
async def runtime_supervisor_status():
    summary = runtime_supervisor_guidance_service.get_summary()["summary"]
    return {
        "ok": True,
        "mode": "runtime_supervisor_status",
        "supervisor_id": summary["supervisor_id"],
        "guidance_status": summary["guidance_status"],
    }


@router.get("/summary")
async def runtime_supervisor_summary():
    return runtime_supervisor_guidance_service.get_summary()


@router.get("/readiness")
async def runtime_supervisor_readiness():
    return runtime_supervisor_guidance_service.get_readiness()


@router.get("/recommended-next-action")
async def runtime_supervisor_next_action():
    return runtime_supervisor_guidance_service.get_recommended_next_action()
