from fastapi import APIRouter
from app.services.conversation_rollover_handoff_service import conversation_rollover_handoff_service
router=APIRouter(prefix='/api/conversation-rollover-handoff',tags=['conversation-rollover-handoff'])
@router.get('/status')
async def conversation_rollover_handoff_status():
    rollovers=conversation_rollover_handoff_service.get_rollovers()['rollovers']
    return {'ok':True,'mode':'conversation_rollover_handoff_status','rollovers_count':len(rollovers),'rollover_status':'conversation_rollover_handoff_ready'}
@router.get('/rollovers')
async def conversation_rollovers(): return conversation_rollover_handoff_service.get_rollovers()
@router.get('/handoffs')
async def provider_handoff_operations(target_project:str|None=None): return conversation_rollover_handoff_service.get_handoffs(target_project)
@router.get('/package')
async def conversation_rollover_handoff_package(): return conversation_rollover_handoff_service.get_rollover_package()
@router.get('/next-rollover-action')
async def next_conversation_rollover_action(): return conversation_rollover_handoff_service.get_next_rollover_action()
