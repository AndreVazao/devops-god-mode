from fastapi import APIRouter
from pydantic import BaseModel

from app.services.vault_deploy_env_planner_service import vault_deploy_env_planner_service

router = APIRouter(prefix="/api/vault-deploy-env-planner", tags=["vault-deploy-env-planner"])


class RegisterSecretPresenceRequest(BaseModel):
    secret_name: str
    provider: str = "unknown"
    scope: str = "owner-andre"
    present: bool = True
    tenant_id: str = "owner-andre"


class ProjectEnvRequest(BaseModel):
    project_id: str
    tenant_id: str = "owner-andre"


@router.get('/status')
async def status():
    return vault_deploy_env_planner_service.get_status()


@router.get('/package')
async def package():
    return vault_deploy_env_planner_service.get_package()


@router.post('/secret-presence')
async def register_secret_presence(payload: RegisterSecretPresenceRequest):
    return vault_deploy_env_planner_service.register_secret_presence(
        secret_name=payload.secret_name,
        provider=payload.provider,
        scope=payload.scope,
        present=payload.present,
        tenant_id=payload.tenant_id,
    )


@router.post('/project-env-manifest')
async def project_env_manifest(payload: ProjectEnvRequest):
    return vault_deploy_env_planner_service.build_project_env_manifest(
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
    )


@router.post('/readiness-report')
async def readiness_report(payload: ProjectEnvRequest):
    return vault_deploy_env_planner_service.build_readiness_report(
        project_id=payload.project_id,
        tenant_id=payload.tenant_id,
    )


@router.get('/readiness-reports')
async def readiness_reports(tenant_id: str = 'owner-andre', project_id: str | None = None, limit: int = 50):
    return vault_deploy_env_planner_service.list_readiness_reports(
        tenant_id=tenant_id,
        project_id=project_id,
        limit=limit,
    )


@router.get('/dashboard')
async def dashboard(tenant_id: str = 'owner-andre'):
    return vault_deploy_env_planner_service.build_dashboard(tenant_id=tenant_id)


@router.post('/seed-demo-baribudos-secrets')
async def seed_demo_baribudos_secrets(tenant_id: str = 'owner-andre'):
    return vault_deploy_env_planner_service.seed_demo_baribudos_secrets(tenant_id=tenant_id)
