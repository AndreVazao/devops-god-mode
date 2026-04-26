from fastapi import APIRouter

from app.services.mobile_start_config_service import mobile_start_config_service

router = APIRouter(prefix="/api/mobile-start-config", tags=["mobile-start-config"])


@router.get('/status')
async def status():
    return mobile_start_config_service.get_status()


@router.get('/package')
async def package():
    return mobile_start_config_service.get_package()


@router.get('/config')
async def config():
    return mobile_start_config_service.read_config()


@router.get('/validate')
async def validate():
    return mobile_start_config_service.validate_config()


@router.get('/launch-plan')
async def launch_plan(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return mobile_start_config_service.build_launch_plan(tenant_id=tenant_id, device_id=device_id)


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return mobile_start_config_service.build_dashboard(tenant_id=tenant_id, device_id=device_id)
