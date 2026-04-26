from fastapi import APIRouter
from pydantic import BaseModel

from app.services.apk_manifest_router_service import apk_manifest_router_service

router = APIRouter(prefix="/api/apk-router", tags=["apk-router"])


class ResolveRequest(BaseModel):
    tenant_id: str = "owner-andre"
    device_id: str = "android-apk"
    prefer: str = "auto"


@router.get('/status')
async def status():
    return apk_manifest_router_service.get_status()


@router.get('/package')
async def package():
    return apk_manifest_router_service.get_package()


@router.get('/resolve')
async def resolve(tenant_id: str = "owner-andre", device_id: str = "android-apk", prefer: str = "auto"):
    return apk_manifest_router_service.resolve(tenant_id=tenant_id, device_id=device_id, prefer=prefer)


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return apk_manifest_router_service.dashboard(tenant_id=tenant_id, device_id=device_id)


@router.post('/resolve')
async def resolve_post(payload: ResolveRequest):
    return apk_manifest_router_service.resolve(
        tenant_id=payload.tenant_id,
        device_id=payload.device_id,
        prefer=payload.prefer,
    )
