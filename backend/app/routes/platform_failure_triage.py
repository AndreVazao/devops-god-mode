from fastapi import APIRouter
from app.services.platform_failure_triage_service import platform_failure_triage_service
router=APIRouter(prefix='/api/platform-failure-triage',tags=['platform-failure-triage'])
@router.get('/status')
async def platform_failure_triage_status():
    failures=platform_failure_triage_service.get_failures()['failures']
    return {'ok':True,'mode':'platform_failure_triage_status','failures_count':len(failures),'triage_status':'platform_failure_triage_ready'}
@router.get('/failures')
async def platform_failures(): return platform_failure_triage_service.get_failures()
@router.get('/decisions')
async def continuation_decisions(target_project:str|None=None): return platform_failure_triage_service.get_continuation_decisions(target_project)
@router.get('/package')
async def platform_failure_triage_package(): return platform_failure_triage_service.get_triage_package()
@router.get('/next-triage-action')
async def next_platform_failure_triage_action(): return platform_failure_triage_service.get_next_triage_action()
