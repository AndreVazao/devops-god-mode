from fastapi import APIRouter
from app.services.pc_mobile_active_session_service import pc_mobile_active_session_service
router=APIRouter(prefix='/api/pc-mobile-active-session',tags=['pc-mobile-active-session'])
@router.get('/status')
async def pc_mobile_active_session_status():
    sessions=pc_mobile_active_session_service.get_sessions()['sessions']
    return {'ok':True,'mode':'pc_mobile_active_session_status','sessions_count':len(sessions),'session_status':'pc_mobile_active_session_ready'}
@router.get('/sessions')
async def pc_mobile_active_sessions(): return pc_mobile_active_session_service.get_sessions()
@router.get('/buffers')
async def buffered_sync_states(target_project:str|None=None): return pc_mobile_active_session_service.get_buffer_states(target_project)
@router.get('/package')
async def pc_mobile_active_session_package(): return pc_mobile_active_session_service.get_session_package()
@router.get('/next-session-action')
async def next_pc_mobile_active_session_action(): return pc_mobile_active_session_service.get_next_session_action()
