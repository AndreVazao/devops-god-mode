from typing import Any, Dict, List

from app.services.adaptation_planner_service import adaptation_planner_service
from app.services.chat_adapter_inventory_service import chat_adapter_inventory_service
from app.services.script_extraction_reuse_service import script_extraction_reuse_service


class ConversationOrganizationService:
    def _inventory_items(self) -> List[Dict[str, Any]]:
        base_items = chat_adapter_inventory_service.get_inventory()["items"]
        synthetic_followups = [
            {
                "conversation_id": "conv_godmode_core_runtime_followup",
                "platform": "chatgpt_web",
                "title": "God Mode core runtime follow-up",
                "alias": "god-mode-core-runtime-followup",
                "project_key": "devops_god_mode",
                "tags": ["backend", "automation", "runtime", "followup"],
                "contains_code": True,
                "inventory_status": "indexed",
            },
            {
                "conversation_id": "conv_baribudos_backend_phase_7",
                "platform": "chatgpt_web",
                "title": "Baribudos Studio backend phase 7",
                "alias": "baribudos-studio-backend-fase-7",
                "project_key": "baribudos_studio",
                "tags": ["backend", "python", "scripts", "continuation"],
                "contains_code": True,
                "inventory_status": "indexed",
            },
        ]
        return base_items + synthetic_followups

    def _scripts_by_conversation(self) -> Dict[str, List[Dict[str, Any]]]:
        scripts = script_extraction_reuse_service.get_extracted_scripts()["scripts"]
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for script in scripts:
            grouped.setdefault(script["conversation_id"], []).append(script)
        return grouped

    def _continuation_targets(self) -> Dict[str, List[str]]:
        adaptation_plans = adaptation_planner_service.get_adaptation_plans()[
            "adaptation_plans"
        ]
        mapping: Dict[str, List[str]] = {}
        for plan in adaptation_plans:
            mapping.setdefault(plan["target_project"], []).append(plan["source_script_id"])
        return mapping

    def get_groups(self) -> Dict[str, Any]:
        items = self._inventory_items()
        scripts_by_conversation = self._scripts_by_conversation()
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for item in items:
            grouped.setdefault(item["project_key"], []).append(item)

        groups = []
        for project_key, project_items in grouped.items():
            project_items = sorted(project_items, key=lambda item: item["conversation_id"])
            conversation_ids = [item["conversation_id"] for item in project_items]
            script_count = sum(
                len(scripts_by_conversation.get(conversation_id, []))
                for conversation_id in conversation_ids
            )
            code_density = "high" if script_count >= 2 else "medium" if script_count == 1 else "low"
            groups.append(
                {
                    "group_id": f"group_{project_key}",
                    "project_key": project_key,
                    "primary_conversation_id": project_items[0]["conversation_id"],
                    "conversation_ids": conversation_ids,
                    "group_summary": f"{project_key} grouped conversations ready for continuation and reuse review.",
                    "code_density": code_density,
                    "organization_status": "grouped",
                }
            )

        groups = sorted(groups, key=lambda item: (item["project_key"] != "devops_god_mode", item["project_key"]))
        return {"ok": True, "mode": "conversation_groups", "groups": groups}

    def get_relations(self) -> Dict[str, Any]:
        items = self._inventory_items()
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for item in items:
            grouped.setdefault(item["project_key"], []).append(item)

        relations = []
        for project_key, project_items in grouped.items():
            ordered = sorted(project_items, key=lambda item: item["conversation_id"])
            for index in range(len(ordered) - 1):
                source = ordered[index]
                target = ordered[index + 1]
                relation_type = (
                    "continuation_candidate"
                    if source["contains_code"] and target["contains_code"]
                    else "related_context"
                )
                relations.append(
                    {
                        "relation_id": f"rel_{source['conversation_id']}_to_{target['conversation_id']}",
                        "source_conversation_id": source["conversation_id"],
                        "target_conversation_id": target["conversation_id"],
                        "relation_type": relation_type,
                        "confidence_score": 0.93 if relation_type == "continuation_candidate" else 0.76,
                        "relation_reason": f"same project_key={project_key} with overlapping tags and probable follow-up flow",
                    }
                )

        return {"ok": True, "mode": "conversation_relations", "relations": relations}

    def get_continuation_signals(self) -> Dict[str, Any]:
        items = self._inventory_items()
        scripts_by_conversation = self._scripts_by_conversation()
        future_project_source_ids = set(
            self._continuation_targets().get("future_project", [])
        )

        signals = []
        for item in items:
            scripts = scripts_by_conversation.get(item["conversation_id"], [])
            matching_future_scripts = [
                script for script in scripts if script["script_id"] in future_project_source_ids
            ]
            signal_type = "archive_candidate"
            signal_reason = "indexed for history only"
            priority = "low"

            if "followup" in item["tags"] or "continuation" in item["tags"]:
                signal_type = "continue_thread"
                signal_reason = "conversation naming and tags indicate direct continuation"
                priority = "high"
            elif matching_future_scripts:
                signal_type = "adapt_for_new_project"
                signal_reason = "conversation contains scripts already referenced by adaptation planner"
                priority = "high"
            elif item["contains_code"]:
                signal_type = "merge_review"
                signal_reason = "conversation contains code and should be compared against neighboring project threads"
                priority = "medium"

            signals.append(
                {
                    "conversation_id": item["conversation_id"],
                    "project_key": item["project_key"],
                    "signal_type": signal_type,
                    "priority": priority,
                    "signal_reason": signal_reason,
                }
            )

        return {
            "ok": True,
            "mode": "conversation_continuation_signals",
            "continuation_signals": sorted(
                signals,
                key=lambda item: {"high": 0, "medium": 1, "low": 2}[item["priority"]],
            ),
        }

    def get_next_focus(self) -> Dict[str, Any]:
        groups = self.get_groups()["groups"]
        signals = self.get_continuation_signals()["continuation_signals"]
        top_signal = signals[0] if signals else None
        top_group = next(
            (
                group
                for group in groups
                if top_signal and group["project_key"] == top_signal["project_key"]
            ),
            groups[0] if groups else None,
        )
        return {
            "ok": True,
            "mode": "conversation_next_focus",
            "next_focus": {
                "project_key": top_group["project_key"] if top_group else None,
                "group_id": top_group["group_id"] if top_group else None,
                "conversation_id": top_signal["conversation_id"] if top_signal else None,
                "recommended_action": top_signal["signal_type"] if top_signal else None,
                "focus_reason": top_signal["signal_reason"] if top_signal else None,
            },
        }


conversation_organization_service = ConversationOrganizationService()
