from fastapi import APIRouter

from app.services.project_bootstrap_cockpit_service import project_bootstrap_cockpit_service

router = APIRouter(prefix="/api/project-bootstrap-cockpit", tags=["project-bootstrap-cockpit"])


@router.get('/status')
async def status():
    return project_bootstrap_cockpit_service.get_status()


@router.get('/package')
async def package():
    return project_bootstrap_cockpit_service.get_package()


@router.get('/dashboard')
async def dashboard(
    tenant_id: str = 'owner-andre',
    project_name: str = 'godmode-project',
    providers: str = 'github,vercel,supabase,render',
    multirepo_mode: bool = True,
):
    provider_list = [item.strip() for item in providers.split(',') if item.strip()]
    return project_bootstrap_cockpit_service.build_dashboard(
        tenant_id=tenant_id,
        project_name=project_name,
        providers=provider_list,
        multirepo_mode=multirepo_mode,
    )
