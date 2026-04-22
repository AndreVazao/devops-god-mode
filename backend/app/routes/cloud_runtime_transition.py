from fastapi import APIRouter
from app.services.cloud_runtime_transition_service import cloud_runtime_transition_service
router=APIRouter(prefix='/api/cloud-runtime-transition',tags=['cloud-runtime-transition'])
@router.get('/status')
async def cloud_runtime_transition_status():
    legacy_stacks=cloud_runtime_transition_service.get_legacy_stacks()['legacy_stacks']
    return {'ok':True,'mode':'cloud_runtime_transition_status','legacy_stacks_count':len(legacy_stacks),'transition_status':'cloud_runtime_transition_ready'}
@router.get('/legacy-stacks')
async def cloud_legacy_stacks(): return cloud_runtime_transition_service.get_legacy_stacks()
@router.get('/cutover-actions')
async def local_first_cutover_actions(target_runtime:str|None=None): return cloud_runtime_transition_service.get_cutover_actions(target_runtime)
@router.get('/package')
async def cloud_runtime_transition_package(): return cloud_runtime_transition_service.get_transition_package()
@router.get('/next-transition-action')
async def next_cloud_runtime_transition_action(): return cloud_runtime_transition_service.get_next_transition_action()
