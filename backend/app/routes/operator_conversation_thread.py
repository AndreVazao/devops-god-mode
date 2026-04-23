from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_conversation_thread_service import operator_conversation_thread_service

router = APIRouter(prefix="/api/operator-conversation-thread", tags=["operator-conversation-thread"])


class OpenThreadRequest(BaseModel):
    tenant_id: str
    conversation_title: str
    channel_mode: str = "mobile_chat"


class AppendMessageRequest(BaseModel):
    thread_id: str
    role: str
    content: str
    operational_state: str = "active"
    suggested_next_steps: list[str] = []


@router.get('/status')
async def status():
    return operator_conversation_thread_service.get_status()


@router.get('/package')
async def package():
    return operator_conversation_thread_service.get_package()


@router.get('/list')
async def list_threads(tenant_id: str | None = None):
    return operator_conversation_thread_service.list_threads(tenant_id=tenant_id)


@router.get('/get/{thread_id}')
async def get_thread(thread_id: str):
    return operator_conversation_thread_service.get_thread(thread_id=thread_id)


@router.post('/open')
async def open_thread(payload: OpenThreadRequest):
    return operator_conversation_thread_service.open_thread(
        tenant_id=payload.tenant_id,
        conversation_title=payload.conversation_title,
        channel_mode=payload.channel_mode,
    )


@router.post('/append')
async def append_message(payload: AppendMessageRequest):
    return operator_conversation_thread_service.append_message(
        thread_id=payload.thread_id,
        role=payload.role,
        content=payload.content,
        operational_state=payload.operational_state,
        suggested_next_steps=payload.suggested_next_steps,
    )
