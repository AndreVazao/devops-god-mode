from fastapi import APIRouter
from pydantic import BaseModel

from app.services.pc_autopilot_loop_service import pc_autopilot_loop_service

router = APIRouter(prefix="/api/pc-autopilot", tags=["pc-autopilot-loop"])


class PcAutopilotConfigureRequest(BaseModel):
    enabled: bool | None = None
    interval_seconds: int | None = None
    tenant_id: str | None = None
    max_rounds_per_cycle: int | None = None
    max_jobs_per_round: int | None = None


class PcAutopilotCycleRequest(BaseModel):
    reason: str = "manual_cycle"


@router.get('/status')
async def status():
    return pc_autopilot_loop_service.get_status()


@router.get('/package')
async def package():
    return pc_autopilot_loop_service.get_package()


@router.get('/latest')
async def latest():
    return pc_autopilot_loop_service.latest()


@router.get('/dashboard')
async def dashboard():
    return pc_autopilot_loop_service.build_dashboard()


@router.post('/configure')
async def configure(payload: PcAutopilotConfigureRequest):
    return pc_autopilot_loop_service.configure(
        enabled=payload.enabled,
        interval_seconds=payload.interval_seconds,
        tenant_id=payload.tenant_id,
        max_rounds_per_cycle=payload.max_rounds_per_cycle,
        max_jobs_per_round=payload.max_jobs_per_round,
    )


@router.post('/cycle')
async def cycle(payload: PcAutopilotCycleRequest):
    return pc_autopilot_loop_service.run_cycle(reason=payload.reason)


@router.post('/start')
async def start():
    return pc_autopilot_loop_service.start()


@router.post('/stop')
async def stop():
    return pc_autopilot_loop_service.stop()
