from fastapi import APIRouter
from app.services.remote_session_persistence_service import remote_session_persistence_service
router=APIRouter(prefix='/api/remote-session-persistence',tags=['remote-session-persistence'])
@router.get('/status')
async def remote_session_persistence_status():
    sessions=remote_session_persistence_service.get_sessions()['sessions']
    return {'ok':True,'mode':'remote_session_persistence_status','sessions_count':len(sessions),'session_status':'remote_session_persistence_ready'}
@router.get('/sessions')
async def remote_sessions(): return remote_session_persistence_service.get_sessions()
@router.get('/actions')
async def remote_session_actions(session_area:str|None=None): return remote_session_persistence_service.get_session_actions(session_area)
@router.get('/package')
async def remote_session_package(): return remote_session_persistence_service.get_session_package()
@router.get('/next-session-action')
async def next_remote_session_action(): return remote_session_persistence_service.get_next_session_action()
