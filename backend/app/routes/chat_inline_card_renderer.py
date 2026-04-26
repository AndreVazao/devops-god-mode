from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_inline_card_renderer_service import chat_inline_card_renderer_service
from app.services.request_orchestrator_service import request_orchestrator_service

router = APIRouter(prefix="/api/chat-inline-card-renderer", tags=["chat-inline-card-renderer"])


class OpenSessionRequest(BaseModel):
    tenant_id: str = "owner-andre"
    title: str = "God Mode APK chat"


class SendMessageRequest(BaseModel):
    message: str
    thread_id: str | None = None
    tenant_id: str = "owner-andre"
    project_id: str = "GOD_MODE"


class OrchestratedSendRequest(BaseModel):
    message: str
    thread_id: str | None = None
    tenant_id: str = "owner-andre"
    project_id: str = "GOD_MODE"
    auto_run: bool = True


@router.get('/status')
async def status():
    return chat_inline_card_renderer_service.get_status()


@router.get('/package')
async def package():
    return chat_inline_card_renderer_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre"):
    return chat_inline_card_renderer_service.build_dashboard(tenant_id=tenant_id)


@router.get('/manifest')
async def manifest(tenant_id: str = "owner-andre"):
    return chat_inline_card_renderer_service.build_manifest(tenant_id=tenant_id)


@router.post('/open-session')
async def open_session(payload: OpenSessionRequest):
    return chat_inline_card_renderer_service.open_session(tenant_id=payload.tenant_id, title=payload.title)


@router.post('/send')
async def send(payload: SendMessageRequest):
    return chat_inline_card_renderer_service.send_message(
        message=payload.message,
        thread_id=payload.thread_id,
        tenant_id=payload.tenant_id,
        project_id=payload.project_id,
    )


@router.post('/send-orchestrated')
async def send_orchestrated(payload: OrchestratedSendRequest):
    return request_orchestrator_service.submit_request(
        request=payload.message,
        tenant_id=payload.tenant_id,
        project_id=payload.project_id,
        thread_id=payload.thread_id,
        auto_run=payload.auto_run,
    )
