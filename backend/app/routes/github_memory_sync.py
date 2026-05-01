from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.github_memory_sync_service import github_memory_sync_service

router = APIRouter(prefix="/api/github-memory-sync", tags=["github-memory-sync"])


class SyncProjectRequest(BaseModel):
    project_name: str = "GOD_MODE"
    commit_message: Optional[str] = None
    memory_repo: str = "AndreVazao/andreos-memory"
    dry_run: bool = False
    files: Optional[List[str]] = None


class RecordRepoWorkRequest(BaseModel):
    project_name: str = "GOD_MODE"
    repo_full_name: str
    summary: str
    result: str = ""
    next_steps: str = ""
    memory_repo: str = "AndreVazao/andreos-memory"
    dry_run: bool = False


@router.get("/status")
async def status():
    return github_memory_sync_service.get_status()


@router.get("/panel")
async def panel():
    return github_memory_sync_service.panel()


@router.get("/policy")
async def policy():
    return github_memory_sync_service.policy()


@router.get("/latest")
async def latest():
    return github_memory_sync_service.latest()


@router.post("/sync-project")
async def sync_project(payload: SyncProjectRequest):
    return await github_memory_sync_service.sync_project(
        project_name=payload.project_name,
        commit_message=payload.commit_message,
        memory_repo=payload.memory_repo,
        dry_run=payload.dry_run,
        files=payload.files,
    )


@router.post("/record-repo-work")
async def record_repo_work(payload: RecordRepoWorkRequest):
    return await github_memory_sync_service.record_repo_work_and_sync(
        project_name=payload.project_name,
        repo_full_name=payload.repo_full_name,
        summary=payload.summary,
        result=payload.result,
        next_steps=payload.next_steps,
        memory_repo=payload.memory_repo,
        dry_run=payload.dry_run,
    )
