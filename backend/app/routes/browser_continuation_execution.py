from fastapi import APIRouter
from app.services.browser_continuation_execution_service import browser_continuation_execution_service
router=APIRouter(prefix='/api/browser-continuation-execution',tags=['browser-continuation-execution'])
@router.get('/status')
async def browser_continuation_execution_status():
    executions=browser_continuation_execution_service.get_executions()['executions']
    return {'ok':True,'mode':'browser_continuation_execution_status','executions_count':len(executions),'execution_status':'browser_continuation_execution_ready'}
@router.get('/executions')
async def browser_continuation_executions(): return browser_continuation_execution_service.get_executions()
@router.get('/prompts')
async def browser_continuation_prompts(target_project:str|None=None): return browser_continuation_execution_service.get_prompts(target_project)
@router.get('/package')
async def browser_continuation_execution_package(): return browser_continuation_execution_service.get_execution_package()
@router.get('/next-execution-action')
async def next_browser_continuation_execution_action(): return browser_continuation_execution_service.get_next_execution_action()
