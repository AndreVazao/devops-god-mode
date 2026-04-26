from fastapi import APIRouter

from app.services.first_usable_release_service import first_usable_release_service

router = APIRouter(prefix="/api/first-usable-release", tags=["first-usable-release"])


@router.get('/status')
async def status():
    return first_usable_release_service.get_status()


@router.get('/package')
async def package():
    return first_usable_release_service.get_package()


@router.get('/plan')
async def plan():
    return first_usable_release_service.build_release_plan()


@router.get('/guide')
async def guide():
    return first_usable_release_service.build_operator_guide()


@router.get('/dashboard')
async def dashboard():
    return first_usable_release_service.build_dashboard()
