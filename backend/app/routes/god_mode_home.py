from fastapi import APIRouter
from pydantic import BaseModel

from app.services.god_mode_home_service import god_mode_home_service

router = APIRouter(prefix="/api/god-mode-home", tags=["god-mode-home"])


class OneTapRequest(BaseModel):
    action_id: str
    project_id: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


class HomeChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    project_id: str = "GOD_MODE"
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return god_mode_home_service.get_status()


@router.get('/package')
async def package():
    return god_mode_home_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre"):
    return god_mode_home_service.build_dashboard(tenant_id=tenant_id)


@router.get('/driving-mode')
async def driving_mode(tenant_id: str = "owner-andre"):
    return god_mode_home_service.driving_mode(tenant_id=tenant_id)


@router.post('/one-tap')
async def one_tap(payload: OneTapRequest):
    return god_mode_home_service.run_one_tap(
        action_id=payload.action_id,
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
    )


@router.post('/chat')
async def chat(payload: HomeChatRequest):
    return god_mode_home_service.chat(
        message=payload.message,
        thread_id=payload.thread_id,
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
    )
