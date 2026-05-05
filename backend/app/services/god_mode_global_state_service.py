from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    """Stable project snapshot and operating model for God Mode."""

    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_188_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def implemented_phases(self) -> List[Dict[str, Any]]:
        phases = [
            (155, "Ecosystem Map Operationalization"), (156, "Ruflo Research Lab Adapter"), (157, "Goal Planner Core"),
            (158, "AI Handoff Security Guard"), (159, "Agent Roles Registry"), (160, "AI Provider Router"),
            (161, "MCP Compatibility Map"), (162, "Real Orchestration Pipeline v1"), (163, "Praison Research Adapter"),
            (164, "Orchestration Playbooks v1"), (165, "Pipeline Persistence + Low-Risk Executor v1"),
            (166, "Execution Modes Engine v1"), (167, "Playbook Templates Library"),
            (168, "GitHub Approved Actions Executor"), (169, "Memory Sync Runtime"),
            (170, "Local Knowledge/RAG Decision v1"), (171, "Provider Outcome Learning"),
            (172, "Home/App Control Surface"), (173, "Home Visual Shell"),
            (174, "Launcher/App Default Home Route"), (175, "Global State + README Refresh + Operating Model"),
            (176, "Cockpit Runtime UX + Execution Logs"), (177, "Project Tree Autorefresh + GOD_MODE Tree"),
            (178, "Module Registry Snapshot + GOD_MODE Tree Integration"),
            (179, "Reality Audit + First Real Install Mission"), (180, "PC Runner + Provider Conversation Proof"),
            (181, "First Install Download Center + PC Proof Checklist UI"),
            (182, "Local Encrypted Vault Contract + First Credential Flow"),
            (183, "Lab Best-Of Work Ally + Workflow Hygiene"),
            (184, "Real Local Encrypted Value Store + Approval Gate"),
            (185, "Vault Deployment Binding + Provider Env Injection Plan"),
            (186, "Provider Env Writers Draft + Dry-Run Apply Gate"),
            (187, "Conversation Requirement Ledger + Request/Decision Reconciliation"),
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 188, "name": "Conversation Ledger Cockpit Cards + Open Requirements Review", "status": "in_progress"})
        return result

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["run FastAPI backend", "track requests vs decisions vs reality evidence", "prepare requirement review cards"]},
            "primary_cockpit": {"device": "android_phone", "role": "remote_operator_cockpit", "entrypoint": "/app/home", "responsibilities": ["review open requirement cards", "mark requests confirmed/open/migrated/obsolete/implemented/rejected", "attach notes/evidence refs"]},
            "canonical_entrypoint": {"route": "/app/home", "conversation_requirement_ledger_package": "/api/conversation-requirement-ledger/package", "conversation_ledger_cockpit_review_package": "/api/conversation-ledger-cockpit-review/package"},
        }

    def conversation_requirement_ledger_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/conversation-requirement-ledger/package", "request_is_source_of_intent": True, "ai_answers_are_proposals_until_confirmed": True, "preserves_direction_changes": True, "realness_requires_evidence": True}

    def conversation_ledger_cockpit_review_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/conversation-ledger-cockpit-review/package",
            "cards_endpoint": "/api/conversation-ledger-cockpit-review/cards",
            "review_endpoint": "/api/conversation-ledger-cockpit-review/review",
            "batch_review_endpoint": "/api/conversation-ledger-cockpit-review/batch-review",
            "summary_endpoint": "/api/conversation-ledger-cockpit-review/summary",
            "history_endpoint": "/api/conversation-ledger-cockpit-review/history",
            "mobile_actions": ["confirmed", "still_open", "migrated", "obsolete", "implemented", "rejected_ai_proposal"],
            "request_led_review": True,
            "evidence_preferred_for_realness": True,
        }

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "project_id": "GOD_MODE", "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml"}

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "god_mode_runtime": {"stores": ["conversation request ledger", "open requirement cards", "operator review decisions", "realness scorecards", "script fingerprints"]}}

    def reality_policy(self) -> Dict[str, Any]:
        return {"status": "phase_188_operator_review", "principle": "Open requirements are not silently forgotten; the Oner reviews cards and marks each request status.", "blocked": ["silently close an operator request", "mark AI proposal as accepted without operator review", "hide migration history"], "required": ["request card", "operator decision", "evidence ref when marking real"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Connect provider proof imports to requirement ledger", "Add visible cockpit page for ledger cards", "Run first real PC install mission"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets", "Use GOD_MODE_TREE.md as official tree artifact", "Delete old phase smoke workflows when advancing"]}

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "latest_merged_phase": 187, "current_phase": 188, "canonical_cockpit_route": "/app/home", "mobile_first": True, "pc_brain": True, "secrets_allowed_in_memory": False, "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "conversation_requirement_ledger_endpoint": "/api/conversation-requirement-ledger/package", "conversation_ledger_cockpit_review_endpoint": "/api/conversation-ledger-cockpit-review/package"}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "conversation_requirement_ledger_model": self.conversation_requirement_ledger_model(), "conversation_ledger_cockpit_review_model": self.conversation_ledger_cockpit_review_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "reality_policy": self.reality_policy(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
