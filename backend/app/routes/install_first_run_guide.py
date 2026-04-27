from fastapi import APIRouter

from app.services.install_first_run_guide_service import install_first_run_guide_service

router = APIRouter(prefix="/api/install-first-run", tags=["install-first-run-guide"])


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return install_first_run_guide_service.get_status(tenant_id=tenant_id)


@router.get('/package')
async def package(tenant_id: str = "owner-andre"):
    return install_first_run_guide_service.get_package(tenant_id=tenant_id)


@router.get('/guide')
async def guide(tenant_id: str = "owner-andre"):
    return install_first_run_guide_service.build_guide(tenant_id=tenant_id)
