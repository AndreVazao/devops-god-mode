from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_chat_real_work_bridge_service import operator_chat_real_work_bridge_service

router = APIRouter(prefix="/api/operator-chat-real-work", tags=["operator-chat-real-work"])


class ChatRealWorkRequest(BaseModel):
    message: str
    tenant_id: str = "owner-andre"
    thread_id: str | None = None
    requested_project: str | None = None
    auto_run: bool = True


@router.get('/status')
async def status():
    return operator_chat_real_work_bridge_service.get_status()


@router.get('/package')
async def package():
    return operator_chat_real_work_bridge_service.get_package()


@router.get('/latest')
async def latest():
    return operator_chat_real_work_bridge_service.latest()


@router.post('/submit')
async def submit(payload: ChatRealWorkRequest):
    return operator_chat_real_work_bridge_service.submit_chat_command(
        message=payload.message,
        tenant_id=payload.tenant_id,
        thread_id=payload.thread_id,
        requested_project=payload.requested_project,
        auto_run=payload.auto_run,
    )
