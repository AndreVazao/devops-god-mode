from fastapi import APIRouter

from app.services.install_run_readiness_service import install_run_readiness_service

router = APIRouter(prefix="/api/install-run-readiness", tags=["install-run-readiness"])


@router.get('/status')
async def status():
    return install_run_readiness_service.get_status()


@router.get('/package')
async def package():
    return install_run_readiness_service.get_package()


@router.get('/report')
async def report():
    return install_run_readiness_service.build_report()


@router.get('/checklist')
async def checklist():
    return install_run_readiness_service.build_checklist()


@router.get('/dashboard')
async def dashboard():
    return install_run_readiness_service.build_dashboard()
