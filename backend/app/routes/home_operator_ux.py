from fastapi import APIRouter

from app.services.home_operator_ux_service import home_operator_ux_service

router = APIRouter(prefix="/api/home-operator-ux", tags=["home-operator-ux"])


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return home_operator_ux_service.get_status(tenant_id=tenant_id)


@router.get('/package')
async def package(tenant_id: str = "owner-andre"):
    return home_operator_ux_service.get_package(tenant_id=tenant_id)


@router.get('/panel')
async def panel(tenant_id: str = "owner-andre"):
    return home_operator_ux_service.build_panel(tenant_id=tenant_id)
