from fastapi import APIRouter

from app.services.god_mode_real_completion_scorecard_service import god_mode_real_completion_scorecard_service

router = APIRouter(prefix="/api/god-mode-completion", tags=["god-mode-completion"])


@router.get('/status')
async def status():
    return god_mode_real_completion_scorecard_service.get_status()


@router.post('/status')
async def post_status():
    return god_mode_real_completion_scorecard_service.get_status()


@router.get('/panel')
async def panel():
    return god_mode_real_completion_scorecard_service.panel()


@router.post('/panel')
async def post_panel():
    return god_mode_real_completion_scorecard_service.panel()


@router.get('/scorecard')
async def scorecard():
    return god_mode_real_completion_scorecard_service.build_scorecard()


@router.post('/scorecard')
async def post_scorecard():
    return god_mode_real_completion_scorecard_service.build_scorecard()


@router.get('/definition-100')
async def definition_100():
    return {
        "ok": True,
        "mode": "god_mode_completion_definition_100",
        "definition": god_mode_real_completion_scorecard_service.definition_of_100_percent(),
    }


@router.post('/definition-100')
async def post_definition_100():
    return {
        "ok": True,
        "mode": "god_mode_completion_definition_100",
        "definition": god_mode_real_completion_scorecard_service.definition_of_100_percent(),
    }


@router.get('/latest')
async def latest():
    return god_mode_real_completion_scorecard_service.latest()


@router.post('/latest')
async def post_latest():
    return god_mode_real_completion_scorecard_service.latest()


@router.get('/package')
async def package():
    return god_mode_real_completion_scorecard_service.get_package()


@router.post('/package')
async def post_package():
    return god_mode_real_completion_scorecard_service.get_package()
