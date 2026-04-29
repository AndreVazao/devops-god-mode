from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.project_memory_registry_service import project_memory_registry_service

router = APIRouter(prefix="/api/project-memory-registry", tags=["project-memory-registry"])


class SeedRequest(BaseModel):
    overwrite_existing: bool = False


class ListProjectsRequest(BaseModel):
    status: Optional[str] = None


class UpsertProjectRequest(BaseModel):
    project: Dict[str, Any]


class SyncMemoryRequest(BaseModel):
    limit: int = 50


@router.get('/status')
async def status():
    return project_memory_registry_service.get_status()


@router.post('/status')
async def post_status():
    return project_memory_registry_service.get_status()


@router.get('/panel')
async def panel():
    return project_memory_registry_service.panel()


@router.post('/panel')
async def post_panel():
    return project_memory_registry_service.panel()


@router.get('/projects')
async def projects(status: Optional[str] = None):
    return project_memory_registry_service.list_projects(status=status)


@router.post('/projects')
async def post_projects(payload: ListProjectsRequest):
    return project_memory_registry_service.list_projects(status=payload.status)


@router.post('/seed')
async def seed(payload: SeedRequest):
    return project_memory_registry_service.seed_defaults(overwrite_existing=payload.overwrite_existing)


@router.post('/upsert')
async def upsert(payload: UpsertProjectRequest):
    return project_memory_registry_service.upsert_project(project=payload.project)


@router.get('/audit')
async def audit():
    return project_memory_registry_service.audit()


@router.post('/audit')
async def post_audit():
    return project_memory_registry_service.audit()


@router.post('/sync-memory')
async def sync_memory(payload: SyncMemoryRequest):
    return project_memory_registry_service.sync_memory_contexts(limit=payload.limit)


@router.get('/latest')
async def latest():
    return project_memory_registry_service.latest()


@router.post('/latest')
async def post_latest():
    return project_memory_registry_service.latest()


@router.get('/package')
async def package():
    return project_memory_registry_service.get_package()


@router.post('/package')
async def post_package():
    return project_memory_registry_service.get_package()
