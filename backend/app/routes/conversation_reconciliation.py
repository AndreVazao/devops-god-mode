from fastapi import APIRouter, HTTPException

from app.services.conversation_reconciliation_service import conversation_reconciliation_service

router = APIRouter(prefix="/api/conversation-reconciliation", tags=["conversation-reconciliation"])


@router.get('/status')
async def status():
    return conversation_reconciliation_service.get_status()


@router.get('/package')
async def package():
    return conversation_reconciliation_service.get_package()


@router.post('/{bundle_id}/reconcile')
async def reconcile(bundle_id: str):
    result = conversation_reconciliation_service.reconcile_bundle(bundle_id)
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail='bundle_not_found')
    return result


@router.get('/{bundle_id}/report')
async def report(bundle_id: str):
    result = conversation_reconciliation_service.get_report(bundle_id)
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail='report_not_found')
    return result
