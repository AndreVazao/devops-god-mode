from typing import Any, Dict, List


class InitialInventoryProjectGraphService:
    def get_inventory_sources(self) -> Dict[str, Any]:
        sources: List[Dict[str, Any]] = [
            {
                "initial_inventory_id": "initial_inventory_chatgpt_01",
                "source_type": "conversation_provider",
                "source_priority": 1,
                "inventory_scope": "chat_titles_threads_project_signals",
                "inventory_status": "queued_for_inventory",
            },
            {
                "initial_inventory_id": "initial_inventory_grok_01",
                "source_type": "conversation_provider",
                "source_priority": 2,
                "inventory_scope": "chat_titles_threads_project_signals",
                "inventory_status": "queued_for_inventory",
            },
            {
                "initial_inventory_id": "initial_inventory_gemini_01",
                "source_type": "conversation_provider",
                "source_priority": 3,
                "inventory_scope": "chat_titles_threads_project_signals",
                "inventory_status": "queued_for_inventory",
            },
            {
                "initial_inventory_id": "initial_inventory_deepseek_01",
                "source_type": "conversation_provider",
                "source_priority": 4,
                "inventory_scope": "chat_titles_threads_project_signals",
                "inventory_status": "queued_for_inventory",
            },
            {
                "initial_inventory_id": "initial_inventory_github_01",
                "source_type": "repository_provider",
                "source_priority": 1,
                "inventory_scope": "repos_stacks_program_types",
                "inventory_status": "queued_for_inventory",
            },
        ]
        return {"ok": True, "mode": "initial_inventory_sources", "sources": sources}

    def get_project_graph_links(self, source_type: str | None = None) -> Dict[str, Any]:
        links: List[Dict[str, Any]] = [
            {
                "project_graph_link_id": "project_graph_link_repo_chat_01",
                "source_type": "repository",
                "source_name": "devops-god-mode",
                "probable_project_name": "DevOps God Mode",
                "link_role": "primary_repo",
                "link_status": "probable_match",
            },
            {
                "project_graph_link_id": "project_graph_link_chatgpt_01",
                "source_type": "conversation_provider",
                "source_name": "chatgpt",
                "probable_project_name": "DevOps God Mode",
                "link_role": "primary_conversation_source",
                "link_status": "probable_match",
            },
            {
                "project_graph_link_id": "project_graph_link_deepseek_01",
                "source_type": "conversation_provider",
                "source_name": "deepseek",
                "probable_project_name": "Bot Farm Headless",
                "link_role": "continuation_source",
                "link_status": "probable_match",
            },
        ]
        if source_type:
            links = [item for item in links if item["source_type"] == source_type]
        return {"ok": True, "mode": "project_graph_links", "links": links}

    def get_inventory_package(self) -> Dict[str, Any]:
        package = {
            "sources": self.get_inventory_sources()["sources"],
            "links": self.get_project_graph_links()["links"],
            "mobile_compact": True,
            "package_status": "initial_inventory_ready",
        }
        return {"ok": True, "mode": "initial_inventory_project_graph_package", "package": package}

    def get_next_inventory_action(self) -> Dict[str, Any]:
        sources = self.get_inventory_sources()["sources"]
        next_source = sorted(sources, key=lambda item: (item["source_priority"], item["source_type"]))[0] if sources else None
        return {
            "ok": True,
            "mode": "next_initial_inventory_action",
            "next_inventory_action": {
                "initial_inventory_id": next_source["initial_inventory_id"],
                "source_type": next_source["source_type"],
                "action": "inventory_source_and_extend_project_graph",
                "inventory_status": next_source["inventory_status"],
            }
            if next_source
            else None,
        }


initial_inventory_project_graph_service = InitialInventoryProjectGraphService()
