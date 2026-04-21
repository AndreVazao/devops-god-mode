from fastapi import APIRouter
from app.services.offline_command_buffering_service import offline_command_buffering_service
router=APIRouter(prefix='/api/offline-command-buffering',tags=['offline-command-buffering'])
@router.get('/status')
async def offline_command_buffering_status():
    buffers=offline_command_buffering_service.get_buffers()['buffers']
    return {'ok':True,'mode':'offline_command_buffering_status','buffers_count':len(buffers),'buffer_status':'offline_command_buffering_ready'}
@router.get('/buffers')
async def offline_command_buffers(): return offline_command_buffering_service.get_buffers()
@router.get('/actions')
async def offline_buffer_actions(buffer_area:str|None=None): return offline_command_buffering_service.get_buffer_actions(buffer_area)
@router.get('/package')
async def offline_buffer_package(): return offline_command_buffering_service.get_buffer_package()
@router.get('/next-buffer-action')
async def next_offline_buffer_action(): return offline_command_buffering_service.get_next_buffer_action()
