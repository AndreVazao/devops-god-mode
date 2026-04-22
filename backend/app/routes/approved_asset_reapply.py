from fastapi import APIRouter
from app.services.approved_asset_reapply_service import approved_asset_reapply_service
router=APIRouter(prefix='/api/approved-asset-reapply',tags=['approved-asset-reapply'])
@router.get('/status')
async def approved_asset_reapply_status():
    sessions=approved_asset_reapply_service.get_reapply_sessions()['sessions']
    return {'ok':True,'mode':'approved_asset_reapply_status','sessions_count':len(sessions),'reapply_status':'approved_asset_reapply_ready'}
@router.get('/sessions')
async def approved_asset_reapply_sessions(): return approved_asset_reapply_service.get_reapply_sessions()
@router.get('/actions')
async def visual_reapply_actions(target_project:str|None=None): return approved_asset_reapply_service.get_reapply_actions(target_project)
@router.get('/package')
async def approved_asset_reapply_package(): return approved_asset_reapply_service.get_reapply_package()
@router.get('/next-reapply-action')
async def next_approved_asset_reapply_action(): return approved_asset_reapply_service.get_next_reapply_action()
