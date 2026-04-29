from fastapi import APIRouter

from app.services.home_launch_command_center_service import home_launch_command_center_service

router = APIRouter(prefix="/api/home-launch", tags=["home-launch"])


@router.get('/status')
async def status():
    return home_launch_command_center_service.get_status()


@router.post('/status')
async def post_status():
    return home_launch_command_center_service.get_status()


@router.get('/panel')
async def panel():
    return home_launch_command_center_service.snapshot()


@router.post('/panel')
async def post_panel():
    return home_launch_command_center_service.snapshot()


@router.get('/latest')
async def latest():
    return home_launch_command_center_service.latest()


@router.post('/latest')
async def post_latest():
    return home_launch_command_center_service.latest()


@router.get('/package')
async def package():
    return home_launch_command_center_service.get_package()


@router.post('/package')
async def post_package():
    return home_launch_command_center_service.get_package()
