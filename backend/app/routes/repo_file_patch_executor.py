from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repo_file_patch_executor_service import repo_file_patch_executor_service

router = APIRouter(prefix="/api/repo-file-patch-executor", tags=["repo-file-patch-executor"])


class ExecuteApprovedPatchRequest(BaseModel):
    plan_id: str
    execution_phrase: str = ""
    open_pr: bool = True
    draft_pr: bool = False
    memory_repo: str = "AndreVazao/andreos-memory"
    dry_run: bool = False


@router.get("/status")
async def status():
    return repo_file_patch_executor_service.get_status()


@router.get("/panel")
async def panel():
    return repo_file_patch_executor_service.panel()


@router.get("/policy")
async def policy():
    return repo_file_patch_executor_service.policy()


@router.get("/latest")
async def latest():
    return repo_file_patch_executor_service.latest()


@router.post("/execute")
async def execute(payload: ExecuteApprovedPatchRequest):
    return await repo_file_patch_executor_service.execute(
        plan_id=payload.plan_id,
        execution_phrase=payload.execution_phrase,
        open_pr=payload.open_pr,
        draft_pr=payload.draft_pr,
        memory_repo=payload.memory_repo,
        dry_run=payload.dry_run,
    )
