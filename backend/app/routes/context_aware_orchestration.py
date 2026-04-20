from fastapi import APIRouter

from app.services.context_aware_orchestration_service import (
    context_aware_orchestration_service,
)

router = APIRouter(prefix="/api/context-orchestration", tags=["context-orchestration"])


@router.get("/status")
async def context_orchestration_status():
    lanes = context_aware_orchestration_service.get_lanes()["lanes"]
    return {
        "ok": True,
        "mode": "context_orchestration_status",
        "lanes_count": len(lanes),
        "orchestration_status": "context_orchestration_ready",
    }


@router.get("/summary")
async def context_orchestration_summary():
    return context_aware_orchestration_service.get_context_summary()


@router.get("/lanes")
async def context_orchestration_lanes():
    return context_aware_orchestration_service.get_lanes()


@router.get("/next-decision")
async def context_orchestration_next_decision():
    return context_aware_orchestration_service.get_next_decision()


@router.get("/action-split")
async def context_orchestration_action_split():
    return context_aware_orchestration_service.get_action_split()


@router.post("/apply-next-decision")
async def context_orchestration_apply_next_decision():
    return context_aware_orchestration_service.apply_next_decision()
