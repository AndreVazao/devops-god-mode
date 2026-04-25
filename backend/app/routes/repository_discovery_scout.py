from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repository_discovery_scout_service import repository_discovery_scout_service

router = APIRouter(prefix="/api/repository-discovery", tags=["repository-discovery"])


class CandidateRequest(BaseModel):
    project_id: str
    repository_full_name: str
    confidence: float = 0.5
    source: str = "manual"
    note: str = ""


class ConfirmCandidateRequest(BaseModel):
    candidate_id: str
    role: str = "unknown"


class RepoProposalRequest(BaseModel):
    project_id: str
    suggested_repo_name: str | None = None


@router.get('/status')
async def status():
    return repository_discovery_scout_service.get_status()


@router.get('/package')
async def package():
    return repository_discovery_scout_service.get_package()


@router.get('/dashboard')
async def dashboard():
    return repository_discovery_scout_service.build_dashboard()


@router.get('/plan/{project_id}')
async def plan(project_id: str):
    return repository_discovery_scout_service.build_search_plan(project_id)


@router.post('/candidates')
async def add_candidate(payload: CandidateRequest):
    return repository_discovery_scout_service.add_candidate(
        project_id=payload.project_id,
        repository_full_name=payload.repository_full_name,
        confidence=payload.confidence,
        source=payload.source,
        note=payload.note,
    )


@router.get('/candidates')
async def candidates(project_id: str | None = None, limit: int = 100):
    return repository_discovery_scout_service.list_candidates(project_id=project_id, limit=limit)


@router.post('/candidates/confirm')
async def confirm_candidate(payload: ConfirmCandidateRequest):
    return repository_discovery_scout_service.confirm_candidate(payload.candidate_id, role=payload.role)


@router.post('/proposal')
async def propose_repo(payload: RepoProposalRequest):
    return repository_discovery_scout_service.propose_new_repo(payload.project_id, payload.suggested_repo_name)


@router.get('/audit/{project_id}')
async def audit(project_id: str):
    return repository_discovery_scout_service.audit_project_repository_state(project_id)
