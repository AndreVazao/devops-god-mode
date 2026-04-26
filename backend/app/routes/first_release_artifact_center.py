from fastapi import APIRouter

from app.services.first_release_artifact_center_service import first_release_artifact_center_service

router = APIRouter(prefix="/api/first-release-artifacts", tags=["first-release-artifacts"])


@router.get('/status')
async def status():
    return first_release_artifact_center_service.get_status()


@router.get('/package')
async def package():
    return first_release_artifact_center_service.get_package()


@router.get('/report')
async def report():
    return first_release_artifact_center_service.build_artifact_report()


@router.get('/dashboard')
async def dashboard():
    return first_release_artifact_center_service.build_dashboard()
