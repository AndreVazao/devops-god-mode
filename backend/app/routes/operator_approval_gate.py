from fastapi import APIRouter
from pydantic import BaseModel

from app.services.operator_approval_gate_service import operator_approval_gate_service

router = APIRouter(prefix="/api/operator-approval-gate", tags=["operator-approval-gate"])


class OperatorApprovalGateCreateRequest(BaseModel):
    tenant_id: str
    thread_id: str
    action_label: str
    action_scope: str
    action_payload_summary: str
    risk_level: str = "medium"


class OperatorApprovalGateResolveRequest(BaseModel):
    gate_id: str
    decision: str


@router.get('/status')
async def status():
    return operator_approval_gate_service.get_status()


@router.get('/package')
async def package():
    return operator_approval_gate_service.get_package()


@router.get('/list')
async def list_gates(tenant_id: str | None = None, thread_id: str | None = None):
    return operator_approval_gate_service.list_gates(tenant_id=tenant_id, thread_id=thread_id)


@router.post('/create')
async def create(payload: OperatorApprovalGateCreateRequest):
    return operator_approval_gate_service.create_gate(
        tenant_id=payload.tenant_id,
        thread_id=payload.thread_id,
        action_label=payload.action_label,
        action_scope=payload.action_scope,
        action_payload_summary=payload.action_payload_summary,
        risk_level=payload.risk_level,
    )


@router.post('/resolve')
async def resolve(payload: OperatorApprovalGateResolveRequest):
    return operator_approval_gate_service.resolve_gate(
        gate_id=payload.gate_id,
        decision=payload.decision,
    )
