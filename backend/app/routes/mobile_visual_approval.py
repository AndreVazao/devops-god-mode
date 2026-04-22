from fastapi import APIRouter
from app.services.mobile_visual_approval_service import mobile_visual_approval_service
router=APIRouter(prefix='/api/mobile-visual-approval',tags=['mobile-visual-approval'])
@router.get('/status')
async def mobile_visual_approval_status():
    sessions=mobile_visual_approval_service.get_visual_sessions()['sessions']
    return {'ok':True,'mode':'mobile_visual_approval_status','sessions_count':len(sessions),'approval_status':'mobile_visual_approval_ready'}
@router.get('/sessions')
async def visual_approval_sessions(): return mobile_visual_approval_service.get_visual_sessions()
@router.get('/decisions')
async def visual_revision_decisions(target_project:str|None=None): return mobile_visual_approval_service.get_revision_decisions(target_project)
@router.get('/package')
async def mobile_visual_approval_package(): return mobile_visual_approval_service.get_visual_package()
@router.get('/next-visual-action')
async def next_mobile_visual_approval_action(): return mobile_visual_approval_service.get_next_visual_action()
