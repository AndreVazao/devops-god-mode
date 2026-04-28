from fastapi import APIRouter

from app.services.home_system_health_service import home_system_health_service

router = APIRouter(prefix="/api/home-system-health", tags=["home-system-health"])


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return home_system_health_service.get_status(tenant_id=tenant_id)


@router.post('/status')
async def post_status(tenant_id: str = "owner-andre"):
    return home_system_health_service.get_status(tenant_id=tenant_id)


@router.get('/package')
async def package(tenant_id: str = "owner-andre"):
    return home_system_health_service.get_package(tenant_id=tenant_id)


@router.post('/package')
async def post_package(tenant_id: str = "owner-andre"):
    return home_system_health_service.get_package(tenant_id=tenant_id)


@router.get('/snapshot')
async def snapshot(tenant_id: str = "owner-andre"):
    return home_system_health_service.build_snapshot(tenant_id=tenant_id)


@router.post('/snapshot')
async def post_snapshot(tenant_id: str = "owner-andre"):
    return home_system_health_service.build_snapshot(tenant_id=tenant_id)
