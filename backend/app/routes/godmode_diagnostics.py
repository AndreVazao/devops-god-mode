from fastapi import APIRouter

from app.services.godmode_diagnostics_service import godmode_diagnostics_service

router = APIRouter(prefix="/api/godmode-diagnostics", tags=["godmode-diagnostics"])


@router.get('/status')
async def status():
    return godmode_diagnostics_service.get_status()


@router.get('/package')
async def package():
    return godmode_diagnostics_service.get_package()


@router.get('/dashboard')
async def dashboard(tenant_id: str = 'owner-andre'):
    return godmode_diagnostics_service.build_dashboard(tenant_id=tenant_id)
