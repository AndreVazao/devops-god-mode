from fastapi import APIRouter
from app.services.inter_provider_handoff_adaptation_service import inter_provider_handoff_adaptation_service
router=APIRouter(prefix='/api/inter-provider-handoff-adaptation',tags=['inter-provider-handoff-adaptation'])
@router.get('/status')
async def inter_provider_handoff_status():
    handoffs=inter_provider_handoff_adaptation_service.get_handoffs()['handoffs']
    return {'ok':True,'mode':'inter_provider_handoff_status','handoffs_count':len(handoffs),'handoff_status':'inter_provider_handoff_ready'}
@router.get('/handoffs')
async def inter_provider_handoffs(): return inter_provider_handoff_adaptation_service.get_handoffs()
@router.get('/adaptations')
async def fragment_adaptations(probable_project_name:str|None=None): return inter_provider_handoff_adaptation_service.get_fragment_adaptations(probable_project_name)
@router.get('/package')
async def inter_provider_handoff_package(): return inter_provider_handoff_adaptation_service.get_handoff_package()
@router.get('/next-handoff-action')
async def next_inter_provider_handoff_action(): return inter_provider_handoff_adaptation_service.get_next_handoff_action()
