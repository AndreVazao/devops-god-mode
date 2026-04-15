from fastapi import APIRouter
from pydantic import BaseModel

from app.services.approval_shell_v1 import approval_shell_v1
from app.services.browser_prompt_builder_v1 import browser_prompt_builder_v1
from app.services.code_intake_parser_v1 import code_intake_parser_v1
from app.services.code_intake_pipeline_v1 import code_intake_pipeline_v1
from app.services.git_ops_plan_v1 import git_ops_plan_v1
from app.services.repo_resolution_engine_v1 import repo_resolution_engine_v1
from app.services.workflow_error_intake_v1 import workflow_error_intake_v1

router = APIRouter(prefix="/ops", tags=["ops"])


class CodeIntakeRequest(BaseModel):
    text: str
    repo_full_name: str | None = None
    preferred_path: str | None = None


class GitOpsPlanRequest(BaseModel):
    repo_full_name: str | None = None
    operation: str | None = None
    target_path: str | None = None
    proposed_branch: str | None = None


class WorkflowErrorRequest(BaseModel):
    source: str | None = None
    repo_full_name: str | None = None
    error_text: str


class ResolutionRequest(BaseModel):
    intake: dict
    registry_context: dict | None = None


class BrowserPromptRequest(BaseModel):
    intake: dict | None = None
    resolution: dict | None = None
    workflow_error: dict | None = None


class IntakePipelineRequest(BaseModel):
    text: str
    repo_full_name: str | None = None
    preferred_path: str | None = None
    proposed_branch: str | None = None
    registry_context: dict | None = None


@router.get("/status")
async def ops_status():
    return {
        "ok": True,
        "code_intake": "v1",
        "git_ops_plan": "v1",
        "workflow_error_intake": "v1",
        "repo_resolution": "v1",
        "browser_prompt_builder": "v1",
        "code_intake_pipeline": "v1",
        "approval_shell": "v1",
    }


@router.post("/code-intake")
async def code_intake(request: CodeIntakeRequest):
    return code_intake_parser_v1.parse(request.model_dump())


@router.post("/git-ops-plan")
async def git_ops_plan(request: GitOpsPlanRequest):
    return git_ops_plan_v1.build(request.model_dump())


@router.post("/workflow-error-intake")
async def workflow_error_intake(request: WorkflowErrorRequest):
    return workflow_error_intake_v1.parse(request.model_dump())


@router.post("/repo-resolution")
async def repo_resolution(request: ResolutionRequest):
    return repo_resolution_engine_v1.resolve(request.model_dump())


@router.post("/browser-prompt")
async def browser_prompt(request: BrowserPromptRequest):
    return browser_prompt_builder_v1.build(request.model_dump())


@router.post("/intake-pipeline")
async def intake_pipeline(request: IntakePipelineRequest):
    return code_intake_pipeline_v1.run(request.model_dump())


@router.post("/approval-shell")
async def approval_shell(request: IntakePipelineRequest):
    pipeline = code_intake_pipeline_v1.run(request.model_dump())
    return approval_shell_v1.build(pipeline)
