from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_autopilot_supervisor_service import chat_autopilot_supervisor_service

router = APIRouter(prefix="/api/chat-autopilot", tags=["chat-autopilot-supervisor"])


class ChatAutopilotRunRequest(BaseModel):
    tenant_id: str = "owner-andre"
    job_id: str | None = None
    reason: str = "manual"
    max_rounds: int | None = None
    max_jobs_per_round: int | None = None


@router.get('/status')
async def status():
    return chat_autopilot_supervisor_service.get_status()


@router.get('/package')
async def package():
    return chat_autopilot_supervisor_service.get_package()


@router.get('/latest')
async def latest():
    return chat_autopilot_supervisor_service.latest()


@router.post('/run')
async def run(payload: ChatAutopilotRunRequest):
    return chat_autopilot_supervisor_service.run_until_blocked_or_idle(
        tenant_id=payload.tenant_id,
        job_id=payload.job_id,
        reason=payload.reason,
        max_rounds=payload.max_rounds,
        max_jobs_per_round=payload.max_jobs_per_round,
    )
