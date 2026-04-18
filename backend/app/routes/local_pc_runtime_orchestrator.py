from fastapi import APIRouter

from app.services.local_pc_runtime_orchestrator_service import (
    local_pc_runtime_orchestrator_service,
)

router = APIRouter(prefix="/api/local-pc-runtime", tags=["local-pc-runtime"])


@router.get("/status")
async def local_pc_runtime_status():
    runtime = local_pc_runtime_orchestrator_service.get_runtime_state()["runtime"]
    return {
        "ok": True,
        "mode": "local_pc_runtime_status",
        "orchestrator_id": runtime["orchestrator_id"],
        "orchestrator_status": runtime["orchestrator_status"],
    }


@router.get("/runtime-state")
async def local_pc_runtime_state():
    return local_pc_runtime_orchestrator_service.get_runtime_state()


@router.get("/startup-sequence")
async def local_pc_startup_sequence():
    return local_pc_runtime_orchestrator_service.get_startup_sequence()


@router.get("/mobile-handoff-state")
async def local_pc_mobile_handoff_state():
    return local_pc_runtime_orchestrator_service.get_mobile_handoff_state()
