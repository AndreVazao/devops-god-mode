from fastapi import APIRouter
from pydantic import BaseModel

from app.services.home_command_wizard_service import home_command_wizard_service

router = APIRouter(prefix="/api/home-command-wizard", tags=["home-command-wizard"])


class HomeCommandWizardRequest(BaseModel):
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


class HomeCommandWizardRunRequest(BaseModel):
    command_id: str
    tenant_id: str = "owner-andre"
    requested_project: str = "GOD_MODE"


@router.get('/status')
async def status(tenant_id: str = "owner-andre"):
    return home_command_wizard_service.get_status(tenant_id=tenant_id)


@router.get('/panel')
async def panel(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return home_command_wizard_service.build_panel(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )


@router.post('/panel')
async def post_panel(payload: HomeCommandWizardRequest):
    return home_command_wizard_service.build_panel(
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.post('/run')
async def run(payload: HomeCommandWizardRunRequest):
    return home_command_wizard_service.run(
        command_id=payload.command_id,
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )


@router.get('/package')
async def package(tenant_id: str = "owner-andre", requested_project: str = "GOD_MODE"):
    return home_command_wizard_service.get_package(
        tenant_id=tenant_id,
        requested_project=requested_project,
    )
