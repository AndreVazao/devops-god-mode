from fastapi import APIRouter, HTTPException

from app.services.conversation_provider_linkage_service import (
    conversation_provider_linkage_service,
)

router = APIRouter(
    prefix="/api/conversation-provider-linkage",
    tags=["conversation-provider-linkage"],
)


@router.get("/status")
async def conversation_provider_status():
    linkages = conversation_provider_linkage_service.get_provider_linkages()["linkages"]
    return {
        "ok": True,
        "mode": "conversation_provider_status",
        "linkages_count": len(linkages),
        "provider_status": "conversation_provider_linkage_ready",
    }


@router.get("/linkages")
async def conversation_provider_linkages():
    return conversation_provider_linkage_service.get_provider_linkages()


@router.get("/actions")
async def conversation_provider_actions(provider_name: str | None = None):
    return conversation_provider_linkage_service.get_provider_actions(provider_name)


@router.get("/package/{provider_name}")
async def conversation_provider_package(provider_name: str):
    try:
        return conversation_provider_linkage_service.get_provider_package(provider_name)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="provider_not_found")


@router.get("/next-provider-action")
async def next_conversation_provider_action():
    return conversation_provider_linkage_service.get_next_provider_action()
