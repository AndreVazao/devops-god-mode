from fastapi import APIRouter
from app.services.multi_file_parsing_placement_service import multi_file_parsing_placement_service
router=APIRouter(prefix='/api/multi-file-parsing-placement',tags=['multi-file-parsing-placement'])
@router.get('/status')
async def multi_file_parsing_status():
    batches=multi_file_parsing_placement_service.get_parsing_batches()['batches']
    return {'ok':True,'mode':'multi_file_parsing_status','batches_count':len(batches),'parsing_status':'multi_file_parsing_ready'}
@router.get('/batches')
async def multi_file_parsing_batches(): return multi_file_parsing_placement_service.get_parsing_batches()
@router.get('/decisions')
async def automatic_placement_decisions(probable_file_name:str|None=None): return multi_file_parsing_placement_service.get_placement_decisions(probable_file_name)
@router.get('/package')
async def multi_file_parsing_package(): return multi_file_parsing_placement_service.get_parsing_package()
@router.get('/next-parsing-action')
async def next_multi_file_parsing_action(): return multi_file_parsing_placement_service.get_next_parsing_action()
