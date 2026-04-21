from fastapi import APIRouter
from app.services.automatic_project_classification_service import automatic_project_classification_service
router=APIRouter(prefix='/api/automatic-project-classification',tags=['automatic-project-classification'])
@router.get('/status')
async def automatic_project_classification_status():
    classifications=automatic_project_classification_service.get_classifications()['classifications']
    return {'ok':True,'mode':'automatic_project_classification_status','classifications_count':len(classifications),'classification_status':'automatic_project_classification_ready'}
@router.get('/classifications')
async def automatic_project_classifications(): return automatic_project_classification_service.get_classifications()
@router.get('/decisions')
async def project_grouping_decisions(source_kind:str|None=None): return automatic_project_classification_service.get_grouping_decisions(source_kind)
@router.get('/package')
async def automatic_project_classification_package(): return automatic_project_classification_service.get_classification_package()
@router.get('/next-classification-action')
async def next_automatic_project_classification_action(): return automatic_project_classification_service.get_next_classification_action()
