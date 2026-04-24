from fastapi import APIRouter
from pydantic import BaseModel

from app.services.memory_core_service import memory_core_service

router = APIRouter(prefix="/api/memory-core", tags=["memory-core"])


class ProjectRequest(BaseModel):
    project_name: str


class DecisionRequest(BaseModel):
    project_name: str
    decision: str
    reason: str = ""


class HistoryRequest(BaseModel):
    project_name: str
    action: str
    result: str = ""


class LastSessionRequest(BaseModel):
    project_name: str
    summary: str
    next_steps: str = ""


class BacklogRequest(BaseModel):
    project_name: str
    task: str
    priority: str = "medium"


@router.get('/status')
async def status():
    return memory_core_service.get_status()


@router.get('/package')
async def package():
    return memory_core_service.get_package()


@router.post('/initialize')
async def initialize():
    return memory_core_service.initialize()


@router.post('/projects')
async def create_project(payload: ProjectRequest):
    return memory_core_service.create_project(payload.project_name)


@router.get('/projects/{project_name}')
async def read_project(project_name: str):
    return memory_core_service.read_project(project_name)


@router.post('/decisions')
async def write_decision(payload: DecisionRequest):
    return memory_core_service.write_decision(payload.project_name, payload.decision, payload.reason)


@router.post('/history')
async def write_history(payload: HistoryRequest):
    return memory_core_service.write_history(payload.project_name, payload.action, payload.result)


@router.post('/last-session')
async def update_last_session(payload: LastSessionRequest):
    return memory_core_service.update_last_session(payload.project_name, payload.summary, payload.next_steps)


@router.post('/backlog')
async def add_backlog(payload: BacklogRequest):
    return memory_core_service.add_backlog_task(payload.project_name, payload.task, payload.priority)


@router.get('/context/{project_name}')
async def compact_context(project_name: str, max_chars: int = 12000):
    return memory_core_service.compact_context(project_name, max_chars=max_chars)


@router.get('/obsidian/{project_name}/{file_name}')
async def obsidian_link(project_name: str, file_name: str = 'MEMORIA_MESTRE.md'):
    return memory_core_service.obsidian_link(project_name, file_name)
