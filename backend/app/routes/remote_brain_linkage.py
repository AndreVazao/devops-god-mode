from fastapi import APIRouter, HTTPException

from app.services.remote_brain_linkage_service import remote_brain_linkage_service

router = APIRouter(
    prefix="/api/remote-brain-linkage",
    tags=["remote-brain-linkage"],
)


@router.get("/status")
async def remote_brain_linkage_status():
    linkages = remote_brain_linkage_service.get_linkages()["linkages"]
    return {
        "ok": True,
        "mode": "remote_brain_linkage_status",
        "linkages_count": len(linkages),
        "linkage_status": "remote_brain_linkage_ready",
    }


@router.get("/linkages")
async def remote_brain_linkages():
    return remote_brain_linkage_service.get_linkages()


@router.get("/intents")
async def remote_brain_intents(source_channel: str | None = None):
    return remote_brain_linkage_service.get_intents(source_channel)


@router.get("/package/{source_channel}")
async def remote_brain_linkage_package(source_channel: str):
    try:
        return remote_brain_linkage_service.get_linkage_package(source_channel)
    except (ValueError, StopIteration):
        raise HTTPException(status_code=404, detail="source_channel_not_found")


@router.get("/next-linkage-action")
async def remote_brain_next_action():
    return remote_brain_linkage_service.get_next_linkage_action()
