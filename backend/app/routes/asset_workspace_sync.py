from fastapi import APIRouter
from app.services.asset_workspace_sync_service import asset_workspace_sync_service
router=APIRouter(prefix='/api/asset-workspace-sync',tags=['asset-workspace-sync'])
@router.get('/status')
async def asset_workspace_sync_status():
    syncs=asset_workspace_sync_service.get_asset_syncs()['syncs']
    return {'ok':True,'mode':'asset_workspace_sync_status','syncs_count':len(syncs),'sync_status':'asset_workspace_sync_ready'}
@router.get('/syncs')
async def asset_syncs(): return asset_workspace_sync_service.get_asset_syncs()
@router.get('/workspaces')
async def workspace_bridges(): return asset_workspace_sync_service.get_workspace_bridges()
@router.get('/previews')
async def asset_previews(target_project:str|None=None): return asset_workspace_sync_service.get_asset_previews(target_project)
@router.get('/package')
async def asset_workspace_sync_package(): return asset_workspace_sync_service.get_sync_package()
@router.get('/next-sync-action')
async def next_asset_workspace_sync_action(): return asset_workspace_sync_service.get_next_sync_action()
