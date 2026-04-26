from fastapi import APIRouter
from pydantic import BaseModel

from app.services.apk_launch_manifest_service import apk_launch_manifest_service

router = APIRouter(prefix="/api/apk-launch", tags=["apk-launch"])


class ApkLaunchRequest(BaseModel):
    tenant_id: str = "owner-andre"
    device_id: str = "android-apk"


@router.get('/status')
async def status():
    return apk_launch_manifest_service.get_status()


@router.get('/package')
async def package():
    return apk_launch_manifest_service.get_package()


@router.get('/manifest')
async def manifest(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return apk_launch_manifest_service.build_manifest(tenant_id=tenant_id, device_id=device_id)


@router.get('/health')
async def health(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return apk_launch_manifest_service.health(tenant_id=tenant_id, device_id=device_id)


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return apk_launch_manifest_service.build_dashboard(tenant_id=tenant_id, device_id=device_id)


@router.post('/launch')
async def launch(payload: ApkLaunchRequest):
    return apk_launch_manifest_service.build_manifest(tenant_id=payload.tenant_id, device_id=payload.device_id)
