from fastapi import APIRouter

from app.services.home_critical_actions_hub_service import home_critical_actions_hub_service

router = APIRouter(prefix="/api/home-critical-actions", tags=["home-critical-actions"])


@router.get('/status')
async def status():
    return home_critical_actions_hub_service.get_status()


@router.post('/status')
async def post_status():
    return home_critical_actions_hub_service.get_status()


@router.get('/panel')
async def panel():
    return home_critical_actions_hub_service.snapshot()


@router.post('/panel')
async def post_panel():
    return home_critical_actions_hub_service.snapshot()


@router.get('/snapshot')
async def snapshot():
    return home_critical_actions_hub_service.snapshot()


@router.post('/snapshot')
async def post_snapshot():
    return home_critical_actions_hub_service.snapshot()


@router.get('/latest')
async def latest():
    return home_critical_actions_hub_service.latest()


@router.post('/latest')
async def post_latest():
    return home_critical_actions_hub_service.latest()


@router.get('/package')
async def package():
    return home_critical_actions_hub_service.get_package()


@router.post('/package')
async def post_package():
    return home_critical_actions_hub_service.get_package()
