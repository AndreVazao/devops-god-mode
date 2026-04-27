from fastapi import APIRouter
from pydantic import BaseModel

from app.services.god_mode_home_service import god_mode_home_service

router = APIRouter(prefix="/api/god-mode-home", tags=["god-mode-home"])


class HomeContinueRequest(BaseModel):
    command_text: str | None = None
    tenant_id: str = "owner-andre"
    requested_project: str | None = None


class HomeChatRequest(BaseModel):
    message: str
    tenant_id: str = "owner-andre"
    requested_project: str | None = None


class ApproveNextRequest(BaseModel):
    tenant_id: str = "owner-andre"
    operator_note: str = "Approved from God Mode Home"


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return god_mode_home_service.get_status(tenant_id=tenant_id)


@router.get('/package')
async def package(tenant_id: str = "owner-andre"):
    return god_mode_home_service.get_package(tenant_id=tenant_id)


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre"):
    return god_mode_home_service.build_dashboard(tenant_id=tenant_id)


@router.get('/driving-mode')
async def driving_mode(tenant_id: str = "owner-andre"):
    return god_mode_home_service.driving_mode(tenant_id=tenant_id)


@router.post('/continue')
async def continue_work(payload: HomeContinueRequest):
    return god_mode_home_service.continue_work(
        command_text=payload.command_text,
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.post('/chat')
async def chat(payload: HomeChatRequest):
    return god_mode_home_service.chat(
        message=payload.message,
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.post('/start-autopilot')
async def start_autopilot():
    return god_mode_home_service.start_autopilot()


@router.post('/stop-autopilot')
async def stop_autopilot():
    return god_mode_home_service.stop_autopilot()


@router.post('/approve-next')
async def approve_next(payload: ApproveNextRequest):
    return god_mode_home_service.approve_next(
        tenant_id=payload.tenant_id,
        operator_note=payload.operator_note,
    )
