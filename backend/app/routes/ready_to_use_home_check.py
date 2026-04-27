from fastapi import APIRouter

from app.services.ready_to_use_home_check_service import ready_to_use_home_check_service

router = APIRouter(prefix="/api/ready-to-use", tags=["ready-to-use-home-check"])


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return ready_to_use_home_check_service.get_status(tenant_id=tenant_id)


@router.get('/package')
async def package(tenant_id: str = "owner-andre"):
    return ready_to_use_home_check_service.get_package(tenant_id=tenant_id)


@router.get('/checklist')
async def checklist(tenant_id: str = "owner-andre"):
    return ready_to_use_home_check_service.build_checklist(tenant_id=tenant_id)
