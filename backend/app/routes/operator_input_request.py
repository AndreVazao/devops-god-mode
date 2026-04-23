from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_input_request_service import operator_input_request_service

router = APIRouter(prefix="/api/operator-input-request", tags=["operator-input-request"])


class OperatorInputCreateRequest(BaseModel):
    tenant_id: str
    thread_id: str
    provider_name: str
    request_kind: str
    title: str
    prompt_text: str
    field_label: str
    field_mode: str = "text"
    is_sensitive: bool = True


class OperatorInputSubmitRequest(BaseModel):
    request_id: str
    submitted_value: str


@router.get('/status')
async def status():
    return operator_input_request_service.get_status()


@router.get('/package')
async def package():
    return operator_input_request_service.get_package()


@router.get('/list')
async def list_requests(tenant_id: str | None = None, thread_id: str | None = None):
    return operator_input_request_service.list_requests(tenant_id=tenant_id, thread_id=thread_id)


@router.post('/create')
async def create(payload: OperatorInputCreateRequest):
    return operator_input_request_service.create_request(
        tenant_id=payload.tenant_id,
        thread_id=payload.thread_id,
        provider_name=payload.provider_name,
        request_kind=payload.request_kind,
        title=payload.title,
        prompt_text=payload.prompt_text,
        field_label=payload.field_label,
        field_mode=payload.field_mode,
        is_sensitive=payload.is_sensitive,
    )


@router.post('/submit')
async def submit(payload: OperatorInputSubmitRequest):
    return operator_input_request_service.submit_request(
        request_id=payload.request_id,
        submitted_value=payload.submitted_value,
    )
