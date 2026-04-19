from typing import Any, Dict, List

from app.services.chat_adapter_inventory_service import chat_adapter_inventory_service


class ScriptExtractionReuseService:
    def _scripts(self) -> List[Dict[str, Any]]:
        inventory = chat_adapter_inventory_service.get_inventory()["items"]
        return [
            {
                "script_id": "script_baribudos_backend_main",
                "conversation_id": inventory[0]["conversation_id"],
                "inferred_filename": "backend/main.py",
                "language": "python",
                "project_key": inventory[0]["project_key"],
                "tags": ["backend", "fastapi", "python"],
                "reuse_score": 0.92,
                "extraction_status": "indexed",
            },
            {
                "script_id": "script_website_ui_shell",
                "conversation_id": inventory[1]["conversation_id"],
                "inferred_filename": "frontend/index.html",
                "language": "html",
                "project_key": inventory[1]["project_key"],
                "tags": ["frontend", "ui", "website"],
                "reuse_score": 0.81,
                "extraction_status": "indexed",
            },
            {
                "script_id": "script_godmode_runtime_supervisor",
                "conversation_id": inventory[2]["conversation_id"],
                "inferred_filename": "backend/app/services/runtime_supervisor_guidance_service.py",
                "language": "python",
                "project_key": inventory[2]["project_key"],
                "tags": ["automation", "runtime", "python"],
                "reuse_score": 0.95,
                "extraction_status": "indexed",
            },
        ]

    def get_extracted_scripts(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "extracted_scripts", "scripts": self._scripts()}

    def get_scripts_by_project(self) -> Dict[str, Any]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for item in self._scripts():
            grouped.setdefault(item["project_key"], []).append(item)
        return {"ok": True, "mode": "scripts_by_project", "projects": grouped}

    def get_reuse_maps(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "reuse_maps",
            "reuse_maps": [
                {
                    "reuse_map_id": "reuse_baribudos_to_godmode_backend",
                    "source_project": "baribudos_studio",
                    "target_project": "devops_god_mode",
                    "source_scripts": ["backend/main.py"],
                    "adaptation_hint": "reuse backend structure and adapt routes to the target runtime.",
                    "reuse_status": "mapped",
                },
                {
                    "reuse_map_id": "reuse_godmode_to_future_projects_runtime",
                    "source_project": "devops_god_mode",
                    "target_project": "future_project",
                    "source_scripts": ["backend/app/services/runtime_supervisor_guidance_service.py"],
                    "adaptation_hint": "reuse runtime supervisor logic and adapt guidance outputs.",
                    "reuse_status": "mapped",
                },
            ],
        }

    def get_best_candidates(self) -> Dict[str, Any]:
        scripts = sorted(self._scripts(), key=lambda item: item["reuse_score"], reverse=True)
        return {
            "ok": True,
            "mode": "script_reuse_best_candidates",
            "best_candidates": scripts[:2],
        }


script_extraction_reuse_service = ScriptExtractionReuseService()
