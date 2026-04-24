from fastapi import APIRouter
from pydantic import BaseModel

from app.services.approved_card_execution_queue_service import approved_card_execution_queue_service

router = APIRouter(prefix="/api/approved-card-execution-queue", tags=["approved-card-execution-queue"])


class IngestCardsRequest(BaseModel):
    tenant_id: str = "owner-andre"
    project_id: str | None = None


class UpdateTaskStatusRequest(BaseModel):
    task_id: str
    status: str
    tenant_id: str = "owner-andre"
    note: str = ""


@router.get('/status')
async def status():
    return approved_card_execution_queue_service.get_status()


@router.get('/package')
async def package():
    return approved_card_execution_queue_service.get_package()


@router.post('/ingest-approved-cards')
async def ingest_approved_cards(payload: IngestCardsRequest):
    return approved_card_execution_queue_service.ingest_approved_cards(
        tenant_id=payload.tenant_id,
        project_id=payload.project_id,
    )


@router.get('/tasks')
async def tasks(
    tenant_id: str = 'owner-andre',
    project_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
):
    return approved_card_execution_queue_service.list_tasks(
        tenant_id=tenant_id,
        project_id=project_id,
        status=status,
        limit=limit,
    )


@router.post('/tasks/status')
async def update_task_status(payload: UpdateTaskStatusRequest):
    return approved_card_execution_queue_service.update_task_status(
        task_id=payload.task_id,
        status=payload.status,
        tenant_id=payload.tenant_id,
        note=payload.note,
    )


@router.get('/dashboard')
async def dashboard(tenant_id: str = 'owner-andre'):
    return approved_card_execution_queue_service.build_dashboard(tenant_id=tenant_id)
