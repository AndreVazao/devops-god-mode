from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    """Stable project snapshot and operating model for God Mode."""

    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_189_v1"

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
            (188, "Conversation Ledger Cockpit Cards + Open Requirements Review"),
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 189, "name": "smol-ai GodMode Reference Adapter + Multi-AI Cockpit Patterns", "status": "in_progress"})
        return result

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["run FastAPI backend", "track requests vs decisions vs reality evidence", "prepare provider panes", "plan prompt broadcast across AI webapps"]},
            "primary_cockpit": {"device": "android_phone", "role": "remote_operator_cockpit", "entrypoint": "/app/home", "responsibilities": ["review open requirement cards", "choose providers", "approve prompt broadcast", "monitor provider answers"]},
            "canonical_entrypoint": {"route": "/app/home", "conversation_ledger_cockpit_review_package": "/api/conversation-ledger-cockpit-review/package", "smol_godmode_reference_adapter_package": "/api/smol-godmode-reference-adapter/package"},
        }

    def smol_godmode_reference_adapter_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/smol-godmode-reference-adapter/package",
            "source_repo": "smol-ai/GodMode",
            "source_role": "ux_reference_not_core_dependency",
            "dependency_added": False,
            "native_first": True,
            "useful_patterns": ["dedicated_multi_ai_browser", "prompt_broadcast", "full_webapp_over_api_when_needed", "provider_toggle_and_saved_layout", "prompt_critic"],
            "not_a_replacement_for": ["backend orchestration", "vault", "PR automation", "deploy gates", "memory architecture"],
        }

    def conversation_ledger_cockpit_review_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/conversation-ledger-cockpit-review/package", "request_led_review": True, "evidence_preferred_for_realness": True}

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "project_id": "GOD_MODE", "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml"}

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "god_mode_runtime": {"stores": ["conversation request ledger", "provider pane manifest", "prompt broadcast contract", "prompt critic policy"]}}

    def reality_policy(self) -> Dict[str, Any]:
        return {"status": "phase_189_reference_to_native", "principle": "External repos can inspire patterns, but God Mode remains native, real and evidence-gated.", "blocked": ["add external dependency blindly", "copy architecture that conflicts with PC brain/mobile cockpit", "treat webapp answer as decision without ledger"], "required": ["reference evaluation", "native adapter", "security policy", "future implementation plan"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Implement Provider Prompt Broadcast + Pane Manifest Runtime", "Visible ledger cockpit page", "Run first real PC install mission"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets", "Use GOD_MODE_TREE.md as official tree artifact", "Delete old phase smoke workflows when advancing"]}

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "latest_merged_phase": 188, "current_phase": 189, "canonical_cockpit_route": "/app/home", "mobile_first": True, "pc_brain": True, "secrets_allowed_in_memory": False, "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "smol_godmode_reference_adapter_endpoint": "/api/smol-godmode-reference-adapter/package"}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "conversation_ledger_cockpit_review_model": self.conversation_ledger_cockpit_review_model(), "smol_godmode_reference_adapter_model": self.smol_godmode_reference_adapter_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "reality_policy": self.reality_policy(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
