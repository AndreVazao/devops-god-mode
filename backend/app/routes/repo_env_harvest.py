from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repo_env_harvest_service import repo_env_harvest_service

router = APIRouter(prefix="/api/repo-env-harvest", tags=["repo-env-harvest"])


class RepoEnvSource(BaseModel):
    source_name: str
    path: str
    env_text: str


class RepoEnvHarvestRequest(BaseModel):
    repository_name: str
    target_project: str
    environment_name: str
    env_sources: list[RepoEnvSource]


@router.get('/status')
async def status():
    return repo_env_harvest_service.get_status()


@router.get('/package')
async def package():
    return repo_env_harvest_service.get_package()


@router.post('/harvest')
async def harvest(payload: RepoEnvHarvestRequest):
    return repo_env_harvest_service.harvest_repo_env_sources(
        repository_name=payload.repository_name,
        target_project=payload.target_project,
        environment_name=payload.environment_name,
        env_sources=[item.model_dump() for item in payload.env_sources],
    )
