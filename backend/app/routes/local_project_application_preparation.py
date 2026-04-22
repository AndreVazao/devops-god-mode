from fastapi import APIRouter
from app.services.local_project_application_preparation_service import local_project_application_preparation_service
router=APIRouter(prefix='/api/local-project-application-preparation',tags=['local-project-application-preparation'])
@router.get('/status')
async def local_project_application_preparation_status():
    preparations=local_project_application_preparation_service.get_preparations()['preparations']
    return {'ok':True,'mode':'local_project_application_preparation_status','preparations_count':len(preparations),'application_status':'local_project_application_preparation_ready'}
@router.get('/preparations')
async def local_project_application_preparations(): return local_project_application_preparation_service.get_preparations()
@router.get('/items')
async def local_application_items(target_project:str|None=None): return local_project_application_preparation_service.get_application_items(target_project)
@router.get('/package')
async def local_project_application_preparation_package(): return local_project_application_preparation_service.get_application_package()
@router.get('/next-application-action')
async def next_local_project_application_action(): return local_project_application_preparation_service.get_next_application_action()
