from fastapi import APIRouter

from app.services.chat_adapter_inventory_service import chat_adapter_inventory_service

router = APIRouter(prefix="/api/chat-inventory", tags=["chat-inventory"])


@router.get("/status")
async def chat_inventory_status():
    adapters = chat_adapter_inventory_service.get_adapters()["adapters"]
    return {
        "ok": True,
        "mode": "chat_inventory_status",
        "adapters_count": len(adapters),
        "inventory_status": "chat_inventory_ready",
    }


@router.get("/adapters")
async def chat_inventory_adapters():
    return chat_adapter_inventory_service.get_adapters()


@router.get("/items")
async def chat_inventory_items():
    return chat_adapter_inventory_service.get_inventory()


@router.get("/aliases")
async def chat_inventory_aliases():
    return chat_adapter_inventory_service.get_aliases()


@router.get("/reuse-candidates")
async def chat_inventory_reuse_candidates():
    return chat_adapter_inventory_service.get_reuse_candidates()
