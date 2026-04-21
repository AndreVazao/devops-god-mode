from typing import Any, Dict, List


class PcFirstCoreExtractionService:
    def get_core_surfaces(self) -> Dict[str, Any]:
        surfaces: List[Dict[str, Any]] = [
            {
                "pc_first_core_id": "pc_first_core_01",
                "core_runtime": "pc_brain_primary",
                "cloud_support_mode": "optional_support_only",
                "extraction_scope": [
                    "brain_runtime",
                    "voice_interpretation",
                    "platform_orchestration",
                    "project_context",
                ],
                "extraction_status": "pc_first_transition_ready",
            },
            {
                "pc_first_core_id": "pc_first_core_02",
                "core_runtime": "apk_thin_client_remote_surface",
                "cloud_support_mode": "relay_or_auxiliary_only",
                "extraction_scope": [
                    "voice_capture",
                    "compact_options",
                    "quick_confirmation",
                ],
                "extraction_status": "thin_client_aligned",
            },
        ]
        return {"ok": True, "mode": "pc_first_core_surfaces", "surfaces": surfaces}

    def get_extraction_actions(self, extraction_area: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = [
            {
                "pc_first_extraction_action_id": "pc_first_extract_brain_01",
                "extraction_area": "brain_runtime",
                "action_type": "move_primary_runtime_to_pc",
                "action_label": "Mover runtime principal para o PC",
                "migration_target": "pc_runtime",
                "action_status": "planned",
            },
            {
                "pc_first_extraction_action_id": "pc_first_extract_voice_01",
                "extraction_area": "voice_interpretation",
                "action_type": "keep_voice_capture_in_apk_and_interpret_in_pc",
                "action_label": "Captar voz no APK e interpretar no PC",
                "migration_target": "pc_runtime",
                "action_status": "planned",
            },
            {
                "pc_first_extraction_action_id": "pc_first_extract_cloud_01",
                "extraction_area": "cloud_support",
                "action_type": "reduce_cloud_to_optional_support",
                "action_label": "Reduzir Vercel, Render e Supabase a apoio opcional",
                "migration_target": "support_only",
                "action_status": "planned",
            },
        ]
        if extraction_area:
            actions = [item for item in actions if item["extraction_area"] == extraction_area]
        return {"ok": True, "mode": "pc_first_extraction_actions", "actions": actions}

    def get_extraction_package(self) -> Dict[str, Any]:
        package = {
            "surfaces": self.get_core_surfaces()["surfaces"],
            "actions": self.get_extraction_actions()["actions"],
            "mobile_compact": True,
            "package_status": "pc_first_transition_ready",
        }
        return {"ok": True, "mode": "pc_first_core_extraction_package", "package": package}

    def get_next_extraction_action(self) -> Dict[str, Any]:
        actions = self.get_extraction_actions()["actions"]
        next_action = actions[0] if actions else None
        return {
            "ok": True,
            "mode": "next_pc_first_extraction_action",
            "next_extraction_action": {
                "pc_first_extraction_action_id": next_action["pc_first_extraction_action_id"],
                "extraction_area": next_action["extraction_area"],
                "action": "continue_pc_first_core_migration",
                "action_status": next_action["action_status"],
            }
            if next_action
            else None,
        }


pc_first_core_extraction_service = PcFirstCoreExtractionService()
