from fastapi import APIRouter
from pydantic import BaseModel

from app.services.first_real_install_launcher_service import first_real_install_launcher_service

router = APIRouter(prefix="/api/first-real-install-launcher", tags=["first-real-install-launcher"])


class FirstRealInstallLauncherRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return first_real_install_launcher_service.get_status(tenant_id=tenant_id)


@router.get('/plan')
async def plan(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return first_real_install_launcher_service.build_plan(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/plan')
async def post_plan(payload: FirstRealInstallLauncherRequest):
    return first_real_install_launcher_service.build_plan(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/package')
async def package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return first_real_install_launcher_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )
