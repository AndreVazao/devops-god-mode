from typing import Any, Dict, List


class ChatAdapterInventoryService:
    def get_adapters(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "chat_frontend_adapters",
            "adapters": [
                {
                    "adapter_id": "adapter_chatgpt_web_primary",
                    "platform": "chatgpt_web",
                    "mode": "web_controlled_frontend",
                    "inventory_capable": True,
                    "extraction_capable": True,
                    "rename_mode": "internal_alias_first",
                    "adapter_status": "adapter_ready",
                }
            ],
        }

    def _inventory_items(self) -> List[Dict[str, Any]]:
        return [
            {
                "conversation_id": "conv_baribudos_backend_06",
                "platform": "chatgpt_web",
                "title": "Baribudos Studio backend phase 6",
                "alias": "baribudos-studio-backend-fase-6",
                "project_key": "baribudos_studio",
                "tags": ["backend", "python", "scripts"],
                "contains_code": True,
                "inventory_status": "indexed",
            },
            {
                "conversation_id": "conv_website_primary",
                "platform": "chatgpt_web",
                "title": "Baribudos website primary",
                "alias": "baribudos-website-primary",
                "project_key": "baribudos_website",
                "tags": ["frontend", "website", "ui"],
                "contains_code": True,
                "inventory_status": "indexed",
            },
            {
                "conversation_id": "conv_godmode_core",
                "platform": "chatgpt_web",
                "title": "God Mode core",
                "alias": "god-mode-core",
                "project_key": "devops_god_mode",
                "tags": ["backend", "automation", "runtime"],
                "contains_code": True,
                "inventory_status": "indexed",
            },
        ]

    def get_inventory(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "conversation_inventory",
            "items": self._inventory_items(),
        }

    def get_aliases(self) -> Dict[str, Any]:
        items = self._inventory_items()
        return {
            "ok": True,
            "mode": "conversation_aliases",
            "aliases": [
                {
                    "conversation_id": item["conversation_id"],
                    "title": item["title"],
                    "alias": item["alias"],
                    "project_key": item["project_key"],
                }
                for item in items
            ],
        }

    def get_reuse_candidates(self) -> Dict[str, Any]:
        items = [item for item in self._inventory_items() if item["contains_code"]]
        return {
            "ok": True,
            "mode": "conversation_reuse_candidates",
            "reuse_candidates": [
                {
                    "conversation_id": item["conversation_id"],
                    "alias": item["alias"],
                    "project_key": item["project_key"],
                    "tags": item["tags"],
                    "reuse_hint": "candidate_for_script_extraction_and_adaptation",
                }
                for item in items
            ],
        }


chat_adapter_inventory_service = ChatAdapterInventoryService()
