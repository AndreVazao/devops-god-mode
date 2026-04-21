from fastapi import APIRouter
from app.services.autonomous_project_continuation_service import autonomous_project_continuation_service
router=APIRouter(prefix='/api/autonomous-project-continuation',tags=['autonomous-project-continuation'])
@router.get('/status')
async def autonomous_project_continuation_status():
    continuations=autonomous_project_continuation_service.get_continuations()['continuations']
    return {'ok':True,'mode':'autonomous_project_continuation_status','continuations_count':len(continuations),'continuation_status':'autonomous_project_continuation_ready'}
@router.get('/continuations')
async def autonomous_project_continuations(): return autonomous_project_continuation_service.get_continuations()
@router.get('/actions')
async def continuation_actions(target_project:str|None=None): return autonomous_project_continuation_service.get_continuation_actions(target_project)
@router.get('/package')
async def autonomous_project_continuation_package(): return autonomous_project_continuation_service.get_continuation_package()
@router.get('/next-continuation-action')
async def next_autonomous_project_continuation_action(): return autonomous_project_continuation_service.get_next_continuation_action()
