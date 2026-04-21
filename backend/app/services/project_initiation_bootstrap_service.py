from typing import Any, Dict, List


class ProjectInitiationBootstrapService:
    def get_initiations(self) -> Dict[str, Any]:
        initiations: List[Dict[str, Any]] = [
            {
                "project_initiation_id": "project_init_chatgpt_01",
                "source_assistant": "chatgpt",
                "proposed_project_name": "DevOps God Mode Voice Bootstrap",
                "bootstrap_mode": "conversation_project_repo",
                "initiation_status": "awaiting_project_confirmation",
            },
            {
                "project_initiation_id": "project_init_chatgpt_02",
                "source_assistant": "chatgpt",
                "proposed_project_name": "AI Conversation Merge Lab",
                "bootstrap_mode": "conversation_project_repo",
                "initiation_status": "planned",
            },
        ]
        return {"ok": True, "mode": "project_initiations", "initiations": initiations}

    def get_bootstrap_steps(self, source_assistant: str | None = None) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = [
            {
                "project_bootstrap_step_id": "project_bootstrap_step_start_conversation_01",
                "source_assistant": "chatgpt",
                "step_type": "start_conversation",
                "target_entity": "conversation",
                "step_label": "Iniciar nova conversa de projeto",
                "step_status": "planned",
            },
            {
                "project_bootstrap_step_id": "project_bootstrap_step_name_project_01",
                "source_assistant": "chatgpt",
                "step_type": "propose_project_name",
                "target_entity": "project",
                "step_label": "Definir nome consistente para o novo projeto",
                "step_status": "planned",
            },
            {
                "project_bootstrap_step_id": "project_bootstrap_step_rename_conversation_01",
                "source_assistant": "chatgpt",
                "step_type": "rename_conversation",
                "target_entity": "conversation",
                "step_label": "Renomear conversa com o nome do projeto",
                "step_status": "planned",
            },
            {
                "project_bootstrap_step_id": "project_bootstrap_step_create_repo_01",
                "source_assistant": "chatgpt",
                "step_type": "create_repo",
                "target_entity": "repository",
                "step_label": "Criar repo nova com o nome do projeto",
                "step_status": "planned",
            },
            {
                "project_bootstrap_step_id": "project_bootstrap_step_link_entities_01",
                "source_assistant": "chatgpt",
                "step_type": "link_conversation_project_repo",
                "target_entity": "project_graph",
                "step_label": "Ligar conversa, projeto e repo ao mesmo contexto",
                "step_status": "planned",
            },
        ]
        if source_assistant:
            steps = [item for item in steps if item["source_assistant"] == source_assistant]
        return {"ok": True, "mode": "project_bootstrap_steps", "steps": steps}

    def get_initiation_package(self, source_assistant: str) -> Dict[str, Any]:
        initiation = next(
            item for item in self.get_initiations()["initiations"] if item["source_assistant"] == source_assistant
        )
        package = {
            "initiation": initiation,
            "steps": self.get_bootstrap_steps(source_assistant)["steps"],
            "mobile_compact": True,
            "package_status": initiation["initiation_status"],
        }
        return {"ok": True, "mode": "project_initiation_package", "package": package}

    def get_next_initiation_action(self) -> Dict[str, Any]:
        initiations = self.get_initiations()["initiations"]
        next_initiation = next(
            (item for item in initiations if item["initiation_status"] == "awaiting_project_confirmation"),
            initiations[0] if initiations else None,
        )
        return {
            "ok": True,
            "mode": "next_project_initiation_action",
            "next_initiation_action": {
                "project_initiation_id": next_initiation["project_initiation_id"],
                "source_assistant": next_initiation["source_assistant"],
                "action": "confirm_project_name_then_bootstrap_conversation_and_repo",
                "initiation_status": next_initiation["initiation_status"],
            }
            if next_initiation
            else None,
        }


project_initiation_bootstrap_service = ProjectInitiationBootstrapService()
