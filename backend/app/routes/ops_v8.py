from fastapi import APIRouter
from pydantic import BaseModel

from app.services.approval_shell_v1 import approval_shell_v1
from app.services.browser_prompt_builder_v1 import browser_prompt_builder_v1
from app.services.code_intake_parser_v1 import code_intake_parser_v1
from app.services.code_intake_pipeline_v1 import code_intake_pipeline_v1
from app.services.git_ops_plan_v1 import git_ops_plan_v1
from app.services.mobile_cockpit_payload_v1 import mobile_cockpit_payload_v1
from app.services.ops_execution_pipeline_v1 import ops_execution_pipeline_v1
from app.services.pr_execution_plan_v1 import pr_execution_plan_v1
from app.services.repo_resolution_engine_v1 import repo_resolution_engine_v1
from app.services.repo_visibility_policy_v1 import repo_visibility_policy_v1
from app.services.workflow_error_intake_v1 import workflow_error_intake_v1
from app.services.workflow_repair_prompt_v1 import workflow_repair_prompt_v1

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


class VisibilityPolicyRequest(BaseModel):
    repo_full_name: str | None = None
    desired_visibility: str | None = None
    lifecycle_mode: str | None = None
    build_strategy: str | None = None
    product_ready: bool | None = None


class PRExecutionPlanRequest(BaseModel):
    repo_full_name: str | None = None
    proposed_branch: str | None = None
    base_branch: str | None = None
    operation: str | None = None
    target_path: str | None = None
    approval_required: bool | None = True


class OpsExecutionPipelineRequest(BaseModel):
    text: str
    repo_full_name: str | None = None
    preferred_path: str | None = None
    proposed_branch: str | None = None
    registry_context: dict | None = None
    desired_visibility: str | None = None
    lifecycle_mode: str | None = None
    build_strategy: str | None = None
    product_ready: bool | None = None
    base_branch: str | None = None


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
        "repo_visibility_policy": "v1",
        "pr_execution_plan": "v1",
        "workflow_repair_prompt": "v1",
        "ops_execution_pipeline": "v1",
        "mobile_cockpit_payload": "v1",
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


@router.post("/repo-visibility-policy")
async def repo_visibility_policy(request: VisibilityPolicyRequest):
    return repo_visibility_policy_v1.plan(request.model_dump())


@router.post("/pr-execution-plan")
async def pr_execution_plan(request: PRExecutionPlanRequest):
    return pr_execution_plan_v1.build(request.model_dump())


@router.post("/workflow-repair-prompt")
async def workflow_repair_prompt(request: WorkflowErrorRequest):
    parsed = workflow_error_intake_v1.parse(request.model_dump())
    return workflow_repair_prompt_v1.build({"workflow_error": parsed})


@router.post("/execution-pipeline")
async def execution_pipeline(request: OpsExecutionPipelineRequest):
    return ops_execution_pipeline_v1.run(request.model_dump())


@router.post("/mobile-cockpit")
async def mobile_cockpit(request: OpsExecutionPipelineRequest):
    execution = ops_execution_pipeline_v1.run(request.model_dump())
    return mobile_cockpit_payload_v1.build({"execution": execution})
