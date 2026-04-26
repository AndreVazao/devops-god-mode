from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_boot_briefing_service import chat_boot_briefing_service

router = APIRouter(prefix="/api/chat-boot-briefing", tags=["chat-boot-briefing"])


class BootRequest(BaseModel):
    tenant_id: str = "owner-andre"
    device_id: str = "android-apk"
    thread_id: str | None = None


@router.get('/status')
async def status():
    return chat_boot_briefing_service.get_status()


@router.get('/package')
async def package():
    return chat_boot_briefing_service.get_package()


@router.get('/briefing')
async def briefing(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return chat_boot_briefing_service.build_briefing(tenant_id=tenant_id, device_id=device_id)


@router.post('/boot')
async def boot(payload: BootRequest):
    return chat_boot_briefing_service.boot_chat(
        tenant_id=payload.tenant_id,
        device_id=payload.device_id,
        thread_id=payload.thread_id,
    )


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return chat_boot_briefing_service.build_dashboard(tenant_id=tenant_id, device_id=device_id)
