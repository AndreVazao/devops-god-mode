from fastapi import APIRouter
from app.services.pc_mobile_runtime_topology_service import pc_mobile_runtime_topology_service
router=APIRouter(prefix='/api/pc-mobile-runtime-topology',tags=['pc-mobile-runtime-topology'])
@router.get('/status')
async def pc_mobile_runtime_topology_status():
    topologies=pc_mobile_runtime_topology_service.get_topologies()['topologies']
    return {'ok':True,'mode':'pc_mobile_runtime_topology_status','topologies_count':len(topologies),'topology_status':'pc_mobile_runtime_topology_ready'}
@router.get('/topologies')
async def pc_mobile_runtime_topologies(): return pc_mobile_runtime_topology_service.get_topologies()
@router.get('/cloud-policies')
async def cloud_dependency_policies(target_stack:str|None=None): return pc_mobile_runtime_topology_service.get_cloud_policies(target_stack)
@router.get('/package')
async def pc_mobile_runtime_topology_package(): return pc_mobile_runtime_topology_service.get_topology_package()
@router.get('/next-topology-action')
async def next_pc_mobile_runtime_topology_action(): return pc_mobile_runtime_topology_service.get_next_topology_action()
