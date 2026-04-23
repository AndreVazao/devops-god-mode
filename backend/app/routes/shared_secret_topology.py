from fastapi import APIRouter
from pydantic import BaseModel

from app.services.shared_secret_topology_service import shared_secret_topology_service

router = APIRouter(prefix="/api/shared-secret-topology", tags=["shared-secret-topology"])


class SharedSecretTopologyRequest(BaseModel):
    project_names: list[str]


@router.get('/status')
async def status():
    return shared_secret_topology_service.get_status()


@router.get('/package')
async def package():
    return shared_secret_topology_service.get_package()


@router.post('/build')
async def build(payload: SharedSecretTopologyRequest):
    return shared_secret_topology_service.build_topology(project_names=payload.project_names)
