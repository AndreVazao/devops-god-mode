from fastapi import APIRouter

from app.services.artifacts_center_service import artifacts_center_service

router = APIRouter(prefix="/api/artifacts-center", tags=["artifacts-center"])


@router.get('/status')
async def status():
    return artifacts_center_service.get_status()


@router.get('/package')
async def package():
    return artifacts_center_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return artifacts_center_service.build_dashboard()
