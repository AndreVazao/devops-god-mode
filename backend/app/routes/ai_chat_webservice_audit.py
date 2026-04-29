from fastapi import APIRouter

from app.services.ai_chat_webservice_audit_service import ai_chat_webservice_audit_service

router = APIRouter(prefix="/api/ai-chat-webservice-audit", tags=["ai-chat-webservice-audit"])


@router.get('/status')
async def status():
    return ai_chat_webservice_audit_service.get_status()


@router.post('/status')
async def post_status():
    return ai_chat_webservice_audit_service.get_status()


@router.get('/audit')
async def audit():
    return ai_chat_webservice_audit_service.build_audit()


@router.post('/audit')
async def post_audit():
    return ai_chat_webservice_audit_service.build_audit()


@router.get('/package')
async def package():
    return ai_chat_webservice_audit_service.get_package()


@router.post('/package')
async def post_package():
    return ai_chat_webservice_audit_service.get_package()
