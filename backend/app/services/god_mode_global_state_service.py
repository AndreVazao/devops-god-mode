from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_195_v1"

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
            (191, "Visible Provider Broadcast Cockpit Page + Manual Response Capture"), (192, "Provider Browser Proof Execution Link + Login Attention Cards"),
            (193, "Real Work Intake Map + First PC Fast Path"), (194, "Repo Scanner Auto-Populate Real Work Map"),
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 195, "name": "GitHub Repo Inventory Connector + Real Work Scanner Feed", "status": "in_progress"})
        return result

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["store sanitized repo inventory", "feed scanner", "persist repo snapshot", "create review cards for unknown repos"]},
            "primary_cockpit": {"device": "android_phone", "role": "remote_operator_cockpit", "entrypoint": "/app/home", "responsibilities": ["import connector repo snapshot", "paste repo list fallback", "review unknown repos", "open repo scanner"]},
            "canonical_entrypoint": {"route": "/app/home", "github_repo_inventory_route": "/app/github-repo-inventory-feed", "github_repo_inventory_package": "/api/github-repo-inventory-feed/package"},
        }

    def github_repo_inventory_feed_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/github-repo-inventory-feed/package",
            "route": "/app/github-repo-inventory-feed",
            "alias": "/app/repo-inventory",
            "features": ["connector snapshot import", "manual repo list fallback", "scanner feed", "repo snapshot persistence", "new/unknown repo cards"],
            "connector_runtime_inside_backend": False,
            "blocked": ["store secrets", "clone repos automatically", "delete repos", "change repo settings", "merge repos"],
        }

    def repo_scanner_real_work_map_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/repo-scanner-real-work-map/package", "route": "/app/repo-scanner-real-work-map", "features": ["repo scan", "group/front suggestion", "website+studio pair detection", "review cards"]}

    def real_work_fast_path_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/real-work-fast-path/package", "route": "/app/real-work-fast-path", "default_groups": ["god_mode", "baribudos_platform", "proventil"]}

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "project_id": "GOD_MODE", "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml"}

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "god_mode_runtime": {"stores": ["sanitized repo inventory", "repo scanner feeds", "new repo cards", "real work map links"]}}

    def reality_policy(self) -> Dict[str, Any]:
        return {"status": "phase_195_github_repo_inventory_feed", "principle": "Repo inventory is metadata only and feeds classification; it never performs destructive GitHub operations.", "blocked": ["store secrets", "clone repos automatically", "delete repos", "change repo settings", "merge repos"], "required": ["sanitized metadata", "scanner feed", "operator review for unknown repos"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Conversation source import automation", "Provider browser proof local launcher", "First PC install operator guide polish"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets", "Use GOD_MODE_TREE.md as official tree artifact", "Delete old phase smoke workflows when advancing"]}

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "latest_merged_phase": 194, "current_phase": 195, "canonical_cockpit_route": "/app/home", "github_repo_inventory_route": "/app/github-repo-inventory-feed", "mobile_first": True, "pc_brain": True, "secrets_allowed_in_memory": False, "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md"}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "real_work_fast_path_model": self.real_work_fast_path_model(), "repo_scanner_real_work_map_model": self.repo_scanner_real_work_map_model(), "github_repo_inventory_feed_model": self.github_repo_inventory_feed_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "reality_policy": self.reality_policy(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
