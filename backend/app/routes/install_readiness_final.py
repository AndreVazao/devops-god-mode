from fastapi import APIRouter
from pydantic import BaseModel

from app.services.install_readiness_final_service import install_readiness_final_service

router = APIRouter(prefix="/api/install-readiness-final", tags=["install-readiness-final"])


class InstallReadinessFinalRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"
    run_deep: bool = True


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return install_readiness_final_service.get_status(tenant_id=tenant_id)


@router.get('/check')
async def check(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE", run_deep: bool = True):
    return install_readiness_final_service.build_check(
        tenant_id=tenant_id,
        requested_project=requested_project,
        run_deep=run_deep,
    )


@router.post('/check')
async def post_check(payload: InstallReadinessFinalRequest):
    return install_readiness_final_service.build_check(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
        run_deep=payload.run_deep,
    )


@router.get('/package')
async def package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return install_readiness_final_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )
