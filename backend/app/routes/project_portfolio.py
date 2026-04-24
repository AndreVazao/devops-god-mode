from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.project_portfolio_service import project_portfolio_service

router = APIRouter(prefix="/api/project-portfolio", tags=["project-portfolio"])


class ProjectRequest(BaseModel):
    project_id: str
    name: str
    goal: str = ""
    category: str = "general"
    priority: str = "medium"
    repositories: List[str] = []


class RepoLinkRequest(BaseModel):
    project_id: str
    repository_full_name: str
    role: str = "unknown"


@router.get('/status')
async def status():
    return project_portfolio_service.get_status()


@router.get('/package')
async def package():
    return project_portfolio_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return project_portfolio_service.build_dashboard()


@router.post('/seed')
async def seed():
    return project_portfolio_service.seed_defaults()


@router.post('/projects')
async def upsert_project(payload: ProjectRequest):
    return project_portfolio_service.upsert_project(
        project_id=payload.project_id,
        name=payload.name,
        goal=payload.goal,
        category=payload.category,
        priority=payload.priority,
        repositories=payload.repositories,
    )


@router.post('/repositories/link')
async def link_repository(payload: RepoLinkRequest):
    return project_portfolio_service.link_repository(
        project_id=payload.project_id,
        repository_full_name=payload.repository_full_name,
        role=payload.role,
    )
