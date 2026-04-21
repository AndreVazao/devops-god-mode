from fastapi import APIRouter
from app.services.initial_inventory_project_graph_service import initial_inventory_project_graph_service
router=APIRouter(prefix='/api/initial-inventory-project-graph',tags=['initial-inventory-project-graph'])
@router.get('/status')
async def initial_inventory_project_graph_status():
    sources=initial_inventory_project_graph_service.get_inventory_sources()['sources']
    return {'ok':True,'mode':'initial_inventory_project_graph_status','sources_count':len(sources),'inventory_status':'initial_inventory_project_graph_ready'}
@router.get('/sources')
async def initial_inventory_sources(): return initial_inventory_project_graph_service.get_inventory_sources()
@router.get('/links')
async def project_graph_links(source_type:str|None=None): return initial_inventory_project_graph_service.get_project_graph_links(source_type)
@router.get('/package')
async def initial_inventory_package(): return initial_inventory_project_graph_service.get_inventory_package()
@router.get('/next-inventory-action')
async def next_initial_inventory_action(): return initial_inventory_project_graph_service.get_next_inventory_action()
