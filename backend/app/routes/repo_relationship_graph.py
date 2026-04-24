from fastapi import APIRouter
from pydantic import BaseModel

from app.services.repo_relationship_graph_service import repo_relationship_graph_service

router = APIRouter(prefix="/api/repo-relationship-graph", tags=["repo-relationship-graph"])


class UpsertRepositoryRequest(BaseModel):
    repository_full_name: str
    project_id: str | None = None
    project_name: str | None = None
    roles: list[str] | None = None
    description: str = ""
    default_branch: str = "main"
    deploy_targets: list[str] | None = None
    tenant_id: str = "owner-andre"


class BuildAuditPlanRequest(BaseModel):
    project_id: str
    tenant_id: str = "owner-andre"
    include_repair_plan: bool = True


@router.get('/status')
async def status():
    return repo_relationship_graph_service.get_status()


@router.get('/package')
async def package():
    return repo_relationship_graph_service.get_package()


@router.post('/repositories')
async def upsert_repository(payload: UpsertRepositoryRequest):
    return repo_relationship_graph_service.upsert_repository(
        repository_full_name=payload.repository_full_name,
        project_id=payload.project_id,
        project_name=payload.project_name,
        roles=payload.roles,
        description=payload.description,
        default_branch=payload.default_branch,
        deploy_targets=payload.deploy_targets,
        tenant_id=payload.tenant_id,
    )


@router.post('/seed-from-conversation-inventory')
async def seed_from_conversation_inventory(tenant_id: str = 'owner-andre'):
    return repo_relationship_graph_service.seed_from_conversation_inventory(tenant_id=tenant_id)


@router.post('/seed-demo-baribudos')
async def seed_demo_baribudos(tenant_id: str = 'owner-andre'):
    return repo_relationship_graph_service.seed_demo_baribudos_graph(tenant_id=tenant_id)


@router.get('/graph')
async def graph(tenant_id: str = 'owner-andre'):
    return repo_relationship_graph_service.build_graph(tenant_id=tenant_id)


@router.get('/dashboard')
async def dashboard(tenant_id: str = 'owner-andre'):
    return repo_relationship_graph_service.build_dashboard(tenant_id=tenant_id)


@router.post('/audit-plan')
async def audit_plan(payload: BuildAuditPlanRequest):
    return repo_relationship_graph_service.build_deep_audit_plan(
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
        include_repair_plan=payload.include_repair_plan,
    )


@router.get('/audit-plans')
async def audit_plans(tenant_id: str = 'owner-andre', project_id: str | None = None, limit: int = 50):
    return repo_relationship_graph_service.list_audit_plans(tenant_id=tenant_id, project_id=project_id, limit=limit)
