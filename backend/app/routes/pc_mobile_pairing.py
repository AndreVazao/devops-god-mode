from fastapi import APIRouter

from app.services.pc_mobile_pairing_service import pc_mobile_pairing_service

router = APIRouter(prefix="/api/pc-mobile-pairing", tags=["pc-mobile-pairing"])


@router.get('/status')
async def status():
    return pc_mobile_pairing_service.get_status()


@router.get('/package')
async def package():
    return pc_mobile_pairing_service.get_package()


@router.get('/pairing')
async def pairing():
    return pc_mobile_pairing_service.build_pairing_package()


@router.get('/dashboard')
async def dashboard():
    return pc_mobile_pairing_service.build_dashboard()
