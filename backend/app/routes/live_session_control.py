from fastapi import APIRouter
from app.services.live_session_control_service import live_session_control_service
router=APIRouter(prefix='/api/live-session-control',tags=['live-session-control'])
@router.get('/status')
async def live_session_control_status():
    controls=live_session_control_service.get_controls()['controls']
    return {'ok':True,'mode':'live_session_control_status','controls_count':len(controls),'control_status':'live_session_control_ready'}
@router.get('/controls')
async def live_session_controls(): return live_session_control_service.get_controls()
@router.get('/recovery-actions')
async def session_recovery_actions(target_project:str|None=None): return live_session_control_service.get_recovery_actions(target_project)
@router.get('/package')
async def live_session_control_package(): return live_session_control_service.get_control_package()
@router.get('/next-control-action')
async def next_live_session_control_action(): return live_session_control_service.get_next_control_action()
