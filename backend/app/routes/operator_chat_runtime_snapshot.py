from fastapi import APIRouter

from app.services.operator_chat_runtime_snapshot_service import operator_chat_runtime_snapshot_service

router = APIRouter(prefix="/api/operator-chat-runtime-snapshot", tags=["operator-chat-runtime-snapshot"])


@router.get('/status')
async def status():
    return operator_chat_runtime_snapshot_service.get_status()


@router.get('/package')
async def package():
    return operator_chat_runtime_snapshot_service.get_package()


@router.get('/snapshot')
async def snapshot(tenant_id: str, thread_id: str | None = None):
    return operator_chat_runtime_snapshot_service.build_snapshot(tenant_id=tenant_id, thread_id=thread_id)
