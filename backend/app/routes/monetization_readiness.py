from fastapi import APIRouter

from app.services.monetization_readiness_service import monetization_readiness_service

router = APIRouter(prefix="/api/monetization-readiness", tags=["monetization-readiness"])


@router.get('/status')
async def status():
    return monetization_readiness_service.get_status()


@router.get('/package')
async def package():
    return monetization_readiness_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return monetization_readiness_service.build_dashboard()


@router.post('/matrix')
async def matrix():
    return monetization_readiness_service.build_matrix()


@router.get('/reports')
async def reports(limit: int = 20):
    return monetization_readiness_service.list_reports(limit=limit)
