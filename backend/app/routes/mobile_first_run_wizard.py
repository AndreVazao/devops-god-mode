from fastapi import APIRouter

from app.services.mobile_first_run_wizard_service import mobile_first_run_wizard_service

router = APIRouter(prefix="/api/mobile-first-run", tags=["mobile-first-run"])


@router.get('/status')
async def status():
    return mobile_first_run_wizard_service.get_status()


@router.get('/package')
async def package():
    return mobile_first_run_wizard_service.get_package()


@router.get('/check')
async def check(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return mobile_first_run_wizard_service.run_check(tenant_id=tenant_id, device_id=device_id)


@router.get('/start')
async def start(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return mobile_first_run_wizard_service.start(tenant_id=tenant_id, device_id=device_id)


@router.get('/dashboard')
async def dashboard(tenant_id: str = "owner-andre", device_id: str = "android-apk"):
    return mobile_first_run_wizard_service.build_dashboard(tenant_id=tenant_id, device_id=device_id)
