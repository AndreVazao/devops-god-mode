from fastapi import APIRouter

from app.services.home_button_selftest_service import home_button_selftest_service

router = APIRouter(prefix="/api/home-button-selftest", tags=["home-button-selftest"])


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return home_button_selftest_service.get_status(tenant_id=tenant_id)


@router.post('/status')
async def post_status(tenant_id: str = "owner-andre"):
    return home_button_selftest_service.get_status(tenant_id=tenant_id)


@router.get('/report')
async def report(tenant_id: str = "owner-andre"):
    return home_button_selftest_service.build_report(tenant_id=tenant_id)


@router.post('/report')
async def post_report(tenant_id: str = "owner-andre"):
    return home_button_selftest_service.build_report(tenant_id=tenant_id)


@router.get('/package')
async def package(tenant_id: str = "owner-andre"):
    return home_button_selftest_service.get_package(tenant_id=tenant_id)


@router.post('/package')
async def post_package(tenant_id: str = "owner-andre"):
    return home_button_selftest_service.get_package(tenant_id=tenant_id)
