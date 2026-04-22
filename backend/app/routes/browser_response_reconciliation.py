from fastapi import APIRouter
from app.services.browser_response_reconciliation_service import browser_response_reconciliation_service
router=APIRouter(prefix='/api/browser-response-reconciliation',tags=['browser-response-reconciliation'])
@router.get('/status')
async def browser_response_reconciliation_status():
    captures=browser_response_reconciliation_service.get_response_captures()['captures']
    return {'ok':True,'mode':'browser_response_reconciliation_status','captures_count':len(captures),'reconciliation_status':'browser_response_reconciliation_ready'}
@router.get('/captures')
async def browser_response_captures(): return browser_response_reconciliation_service.get_response_captures()
@router.get('/reconciliations')
async def project_reconciliations(target_project:str|None=None): return browser_response_reconciliation_service.get_reconciliations(target_project)
@router.get('/package')
async def browser_response_reconciliation_package(): return browser_response_reconciliation_service.get_reconciliation_package()
@router.get('/next-reconciliation-action')
async def next_browser_response_reconciliation_action(): return browser_response_reconciliation_service.get_next_reconciliation_action()
