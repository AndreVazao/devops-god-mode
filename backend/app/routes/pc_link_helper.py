from fastapi import APIRouter

from app.services.pc_link_helper_service import pc_link_helper_service

router = APIRouter(prefix="/api/pc-link-helper", tags=["pc-link-helper"])


@router.get('/status')
async def status():
    return pc_link_helper_service.get_status()


@router.get('/panel')
async def panel(port: int = 8000):
    return pc_link_helper_service.build_panel(port=port)


@router.get('/package')
async def package():
    return pc_link_helper_service.get_package()
