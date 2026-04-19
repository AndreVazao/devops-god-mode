from fastapi import APIRouter

from app.services.conversation_organization_service import (
    conversation_organization_service,
)

router = APIRouter(
    prefix="/api/conversation-organization", tags=["conversation-organization"]
)


@router.get("/status")
async def conversation_organization_status():
    groups = conversation_organization_service.get_groups()["groups"]
    return {
        "ok": True,
        "mode": "conversation_organization_status",
        "groups_count": len(groups),
        "organization_status": "conversation_organization_ready",
    }


@router.get("/groups")
async def conversation_organization_groups():
    return conversation_organization_service.get_groups()


@router.get("/relations")
async def conversation_organization_relations():
    return conversation_organization_service.get_relations()


@router.get("/continuation-signals")
async def conversation_organization_continuation_signals():
    return conversation_organization_service.get_continuation_signals()


@router.get("/next-focus")
async def conversation_organization_next_focus():
    return conversation_organization_service.get_next_focus()
