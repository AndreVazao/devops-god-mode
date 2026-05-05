from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_192_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def implemented_phases(self) -> List[Dict[str, Any]]:
        phases = [
            (155, "Ecosystem Map Operationalization"), (156, "Ruflo Research Lab Adapter"), (157, "Goal Planner Core"),
            (158, "AI Handoff Security Guard"), (159, "Agent Roles Registry"), (160, "AI Provider Router"),
            (161, "MCP Compatibility Map"), (162, "Real Orchestration Pipeline v1"), (163, "Praison Research Adapter"),
            (164, "Orchestration Playbooks v1"), (165, "Pipeline Persistence + Low-Risk Executor v1"),
            (166, "Execution Modes Engine v1"), (167, "Playbook Templates Library"), (168, "GitHub Approved Actions Executor"),
            (169, "Memory Sync Runtime"), (170, "Local Knowledge/RAG Decision v1"), (171, "Provider Outcome Learning"),
            (172, "Home/App Control Surface"), (173, "Home Visual Shell"), (174, "Launcher/App Default Home Route"),
            (175, "Global State + README Refresh + Operating Model"), (176, "Cockpit Runtime UX + Execution Logs"),
            (177, "Project Tree Autorefresh + GOD_MODE Tree"), (178, "Module Registry Snapshot + GOD_MODE Tree Integration"),
            (179, "Reality Audit + First Real Install Mission"), (180, "PC Runner + Provider Conversation Proof"),
            (181, "First Install Download Center + PC Proof Checklist UI"), (182, "Local Encrypted Vault Contract + First Credential Flow"),
            (183, "Lab Best-Of Work Ally + Workflow Hygiene"), (184, "Real Local Encrypted Value Store + Approval Gate"),
            (185, "Vault Deployment Binding + Provider Env Injection Plan"), (186, "Provider Env Writers Draft + Dry-Run Apply Gate"),
            (187, "Conversation Requirement Ledger + Request/Decision Reconciliation"), (188, "Conversation Ledger Cockpit Cards + Open Requirements Review"),
            (189, "smol-ai GodMode Reference Adapter + Multi-AI Cockpit Patterns"), (190, "Provider Prompt Broadcast + Pane Manifest Runtime"),
            (191, "Visible Provider Broadcast Cockpit Page + Manual Response Capture"),
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 192, "name": "Provider Browser Proof Execution Link + Login Attention Cards", "status": "in_progress"})
        return result

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["serve broadcast cockpit", "prepare safe provider open links", "create login attention cards", "keep browser automation gated"]},
            "primary_cockpit": {"device": "android_phone", "role": "remote_operator_cockpit", "entrypoint": "/app/home", "responsibilities": ["choose providers", "open provider links manually", "ack login cards", "paste provider answers"]},
            "canonical_entrypoint": {"route": "/app/home", "provider_broadcast_cockpit_route": "/app/provider-broadcast-cockpit", "provider_browser_proof_link_package": "/api/provider-browser-proof-link/package"},
        }

    def provider_browser_proof_link_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/provider-browser-proof-link/package",
            "build_links_endpoint": "/api/provider-browser-proof-link/build-links",
            "create_login_cards_endpoint": "/api/provider-browser-proof-link/create-login-cards",
            "create_automation_gate_endpoint": "/api/provider-browser-proof-link/create-automation-gate",
            "dashboard_endpoint": "/api/provider-browser-proof-link/dashboard",
            "manual_open_enabled": True,
            "browser_automation_enabled": False,
            "stores_credentials": False,
            "stores_cookies": False,
            "requires_gate_for_real_browser_automation": True,
        }

    def visible_provider_broadcast_cockpit_model(self) -> Dict[str, Any]:
        return {"route": "/app/provider-broadcast-cockpit", "manual_capture_enabled": True, "manual_provider_open_enabled": True, "answers_are_decisions": False}

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "project_id": "GOD_MODE", "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml"}

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "god_mode_runtime": {"stores": ["provider proof links", "login attention cards", "browser automation gates", "manual provider response imports"]}}

    def reality_policy(self) -> Dict[str, Any]:
        return {"status": "phase_192_manual_browser_proof", "principle": "Provider browser proof is safe/manual now; real automation needs explicit future gate and proof.", "blocked": ["store provider credentials", "store cookies", "automate login", "send prompts automatically", "scrape private chats without approved proof"], "required": ["safe open link", "login attention card", "operator manual login", "future gate for automation"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Provider browser proof local launcher", "First real PC install mission", "Visible ledger/provider comparison refinements"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets", "Use GOD_MODE_TREE.md as official tree artifact", "Delete old phase smoke workflows when advancing"]}

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "latest_merged_phase": 191, "current_phase": 192, "canonical_cockpit_route": "/app/home", "provider_broadcast_cockpit_route": "/app/provider-broadcast-cockpit", "provider_browser_proof_link_endpoint": "/api/provider-browser-proof-link/package", "mobile_first": True, "pc_brain": True, "secrets_allowed_in_memory": False, "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md"}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "visible_provider_broadcast_cockpit_model": self.visible_provider_broadcast_cockpit_model(), "provider_browser_proof_link_model": self.provider_browser_proof_link_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "reality_policy": self.reality_policy(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
