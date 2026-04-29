from fastapi import APIRouter

from app.services.spectacular_upgrade_advisor_service import spectacular_upgrade_advisor_service

router = APIRouter(prefix="/api/spectacular-upgrade-advisor", tags=["spectacular-upgrade-advisor"])


@router.get('/status')
async def status():
    return spectacular_upgrade_advisor_service.get_status()


@router.post('/status')
async def post_status():
    return spectacular_upgrade_advisor_service.get_status()


@router.get('/panel')
async def panel():
    return spectacular_upgrade_advisor_service.panel()


@router.post('/panel')
async def post_panel():
    return spectacular_upgrade_advisor_service.panel()


@router.get('/report')
async def report():
    return spectacular_upgrade_advisor_service.report()


@router.post('/report')
async def post_report():
    return spectacular_upgrade_advisor_service.report()


@router.get('/phase-plan')
async def phase_plan():
    return spectacular_upgrade_advisor_service.phase_plan()


@router.post('/phase-plan')
async def post_phase_plan():
    return spectacular_upgrade_advisor_service.phase_plan()


@router.get('/latest')
async def latest():
    return spectacular_upgrade_advisor_service.latest()


@router.post('/latest')
async def post_latest():
    return spectacular_upgrade_advisor_service.latest()


@router.get('/package')
async def package():
    return spectacular_upgrade_advisor_service.get_package()


@router.post('/package')
async def post_package():
    return spectacular_upgrade_advisor_service.get_package()
