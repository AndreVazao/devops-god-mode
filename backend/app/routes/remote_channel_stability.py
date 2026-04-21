from fastapi import APIRouter
from app.services.remote_channel_stability_service import remote_channel_stability_service
router=APIRouter(prefix='/api/remote-channel-stability',tags=['remote-channel-stability'])
@router.get('/status')
async def remote_channel_stability_status():
    channels=remote_channel_stability_service.get_channels()['channels']
    return {'ok':True,'mode':'remote_channel_stability_status','channels_count':len(channels),'channel_status':'remote_channel_stability_ready'}
@router.get('/channels')
async def remote_channel_channels(): return remote_channel_stability_service.get_channels()
@router.get('/actions')
async def remote_channel_actions(channel_area:str|None=None): return remote_channel_stability_service.get_channel_actions(channel_area)
@router.get('/package')
async def remote_channel_package(): return remote_channel_stability_service.get_channel_package()
@router.get('/next-channel-action')
async def next_remote_channel_action(): return remote_channel_stability_service.get_next_channel_action()
