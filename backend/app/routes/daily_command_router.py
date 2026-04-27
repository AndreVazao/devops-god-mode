from fastapi import APIRouter
from pydantic import BaseModel

from app.services.daily_command_router_service import daily_command_router_service

router = APIRouter(prefix="/api/daily-command-router", tags=["daily-command-router"])


class DailyCommandRouteRequest(BaseModel):
    command_id: str
    tenant_id: str = "owner-andre"
    requested_project: str | None = None


@router.get('/status')
async def status():
    return daily_command_router_service.get_status()


@router.get('/package')
async def package():
    return daily_command_router_service.get_package()


@router.get('/commands')
async def commands():
    return daily_command_router_service.available_commands()


@router.post('/route')
async def route(payload: DailyCommandRouteRequest):
    return daily_command_router_service.route(
        command_id=payload.command_id,
        tenant_id=payload.tenant_id,
        requested_project=payload.requested_project,
    )
