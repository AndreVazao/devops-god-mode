from fastapi import APIRouter
from app.services.local_project_application_execution_service import local_project_application_execution_service
router=APIRouter(prefix='/api/local-project-application-execution',tags=['local-project-application-execution'])
@router.get('/status')
async def local_project_application_execution_status():
    executions=local_project_application_execution_service.get_executions()['executions']
    return {'ok':True,'mode':'local_project_application_execution_status','executions_count':len(executions),'execution_status':'local_project_application_execution_ready'}
@router.get('/executions')
async def local_project_application_executions(): return local_project_application_execution_service.get_executions()
@router.get('/safeguards')
async def local_apply_safeguards(target_project:str|None=None): return local_project_application_execution_service.get_safeguards(target_project)
@router.get('/package')
async def local_project_application_execution_package(): return local_project_application_execution_service.get_execution_package()
@router.get('/next-execution-action')
async def next_local_project_application_execution_action(): return local_project_application_execution_service.get_next_execution_action()
