from fastapi import APIRouter
from app.services.mobile_cockpit_sync_service import mobile_cockpit_sync_service
router=APIRouter(prefix='/api/mobile-cockpit-sync',tags=['mobile-cockpit-sync'])
@router.get('/status')
async def mobile_cockpit_sync_status():
    commands=mobile_cockpit_sync_service.get_mobile_commands()['commands']
    return {'ok':True,'mode':'mobile_cockpit_sync_status','commands_count':len(commands),'sync_status':'mobile_cockpit_sync_ready'}
@router.get('/commands')
async def mobile_cockpit_commands(): return mobile_cockpit_sync_service.get_mobile_commands()
@router.get('/results')
async def mobile_cockpit_results(target_project:str|None=None): return mobile_cockpit_sync_service.get_mobile_results(target_project)
@router.get('/package')
async def mobile_cockpit_sync_package(): return mobile_cockpit_sync_service.get_sync_package()
@router.get('/next-sync-action')
async def next_mobile_cockpit_sync_action(): return mobile_cockpit_sync_service.get_next_sync_action()
