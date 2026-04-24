from fastapi import APIRouter

from app.services.godmode_remediation_service import godmode_remediation_service

router = APIRouter(prefix="/api/godmode-remediation", tags=["godmode-remediation"])


@router.get('/status')
async def status():
    return godmode_remediation_service.get_status()


@router.get('/package')
async def package():
    return godmode_remediation_service.get_package()


@router.get('/plan')
async def plan(tenant_id: str = 'owner-andre'):
    return godmode_remediation_service.build_plan(tenant_id=tenant_id)
