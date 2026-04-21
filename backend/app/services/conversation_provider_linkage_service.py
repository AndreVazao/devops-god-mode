from typing import Any, Dict, List


class ConversationProviderLinkageService:
    def get_provider_linkages(self) -> Dict[str, Any]:
        linkages: List[Dict[str, Any]] = [
            {
                "conversation_provider_linkage_id": "provider_linkage_chatgpt_01",
                "provider_name": "chatgpt",
                "provider_scope": ["new_conversation", "project_naming", "conversation_organization"],
                "linkage_mode": "pc_brain_orchestrated",
                "linkage_status": "planned_provider_integration",
            },
            {
                "conversation_provider_linkage_id": "provider_linkage_other_ai_01",
                "provider_name": "other_ai",
                "provider_scope": ["new_conversation", "conversation_organization"],
                "linkage_mode": "pc_brain_orchestrated",
                "linkage_status": "planned_provider_integration",
            },
        ]
        return {"ok": True, "mode": "conversation_provider_linkages", "linkages": linkages}

    def get_provider_actions(self, provider_name: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "conversation_provider_action_id": "provider_action_chatgpt_01",
                "provider_name": "chatgpt",
                "action_type": "start_named_project_conversation",
                "action_label": "Iniciar conversa nova no ChatGPT e propor nome do projeto",
                "target_mode": "conversation_project_repo",
                "action_status": "planned",
            },
            {
                "conversation_provider_action_id": "provider_action_chatgpt_02",
                "provider_name": "chatgpt",
                "action_type": "rename_conversation_from_project_name",
                "action_label": "Renomear conversa com o nome do projeto sugerido",
                "target_mode": "conversation_project_repo",
                "action_status": "planned",
            },
            {
                "conversation_provider_action_id": "provider_action_chatgpt_03",
                "provider_name": "chatgpt",
                "action_type": "create_repo_from_project_name",
                "action_label": "Criar repo nova a partir do nome do projeto",
                "target_mode": "conversation_project_repo",
                "action_status": "planned",
            },
        ]
        if provider_name:
            actions = [item for item in actions if item["provider_name"] == provider_name]
        return {"ok": True, "mode": "conversation_provider_actions", "actions": actions}

    def get_provider_package(self, provider_name: str) -> Dict[str, Any]:
        linkage = next(
            item for item in self.get_provider_linkages()["linkages"] if item["provider_name"] == provider_name
        )
        package = {
            "linkage": linkage,
            "actions": self.get_provider_actions(provider_name)["actions"],
            "mobile_compact": True,
            "package_status": linkage["linkage_status"],
        }
        return {"ok": True, "mode": "conversation_provider_package", "package": package}

    def get_next_provider_action(self) -> Dict[str, Any]:
        actions = self.get_provider_actions()["actions"]
        next_action = actions[0] if actions else None
        return {
            "ok": True,
            "mode": "next_conversation_provider_action",
            "next_provider_action": {
                "conversation_provider_action_id": next_action["conversation_provider_action_id"],
                "provider_name": next_action["provider_name"],
                "action": "prepare_real_provider_conversation_bootstrap",
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


conversation_provider_linkage_service = ConversationProviderLinkageService()
