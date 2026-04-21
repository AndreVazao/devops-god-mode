from fastapi import APIRouter
from app.services.local_runtime_dominance_service import local_runtime_dominance_service
router=APIRouter(prefix='/api/local-runtime-dominance',tags=['local-runtime-dominance'])
@router.get('/status')
async def local_runtime_dominance_status():
    surfaces=local_runtime_dominance_service.get_dominance_surfaces()['surfaces']
    return {'ok':True,'mode':'local_runtime_dominance_status','surfaces_count':len(surfaces),'local_runtime_status':'local_runtime_dominance_ready'}
@router.get('/surfaces')
async def local_runtime_surfaces(): return local_runtime_dominance_service.get_dominance_surfaces()
@router.get('/actions')
async def local_runtime_actions(runtime_area:str|None=None): return local_runtime_dominance_service.get_runtime_actions(runtime_area)
@router.get('/package')
async def local_runtime_package(): return local_runtime_dominance_service.get_dominance_package()
@router.get('/next-runtime-action')
async def next_local_runtime_action(): return local_runtime_dominance_service.get_next_runtime_action()
