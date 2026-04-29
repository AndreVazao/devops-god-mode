from fastapi import APIRouter

from app.services.local_tool_capability_scan_service import local_tool_capability_scan_service

router = APIRouter(prefix="/api/local-tool-capability", tags=["local-tool-capability"])


@router.get('/status')
async def status():
    return local_tool_capability_scan_service.get_status()


@router.post('/status')
async def post_status():
    return local_tool_capability_scan_service.get_status()


@router.get('/panel')
async def panel():
    return local_tool_capability_scan_service.panel()


@router.post('/panel')
async def post_panel():
    return local_tool_capability_scan_service.panel()


@router.get('/scan')
async def scan():
    return local_tool_capability_scan_service.scan()


@router.post('/scan')
async def post_scan():
    return local_tool_capability_scan_service.scan()


@router.get('/plan')
async def plan():
    return local_tool_capability_scan_service.plan()


@router.post('/plan')
async def post_plan():
    return local_tool_capability_scan_service.plan()


@router.get('/latest')
async def latest():
    return local_tool_capability_scan_service.latest()


@router.post('/latest')
async def post_latest():
    return local_tool_capability_scan_service.latest()


@router.get('/package')
async def package():
    return local_tool_capability_scan_service.get_package()


@router.post('/package')
async def post_package():
    return local_tool_capability_scan_service.get_package()
