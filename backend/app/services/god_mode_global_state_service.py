from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    """Stable project snapshot and operating model for God Mode.

    This service is intentionally documentation-as-runtime: the cockpit can ask
    the backend what exists, how it should be operated, what is blocked, and
    what the next roadmap items are.
    """

    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_179_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def implemented_phases(self) -> List[Dict[str, Any]]:
        return [
            {"phase": 155, "name": "Ecosystem Map Operationalization", "status": "merged"},
            {"phase": 156, "name": "Ruflo Research Lab Adapter", "status": "merged", "role": "lab_reference"},
            {"phase": 157, "name": "Goal Planner Core", "status": "merged"},
            {"phase": 158, "name": "AI Handoff Security Guard", "status": "merged"},
            {"phase": 159, "name": "Agent Roles Registry", "status": "merged"},
            {"phase": 160, "name": "AI Provider Router", "status": "merged"},
            {"phase": 161, "name": "MCP Compatibility Map", "status": "merged"},
            {"phase": 162, "name": "Real Orchestration Pipeline v1", "status": "merged"},
            {"phase": 163, "name": "Praison Research Adapter", "status": "merged", "role": "lab_reference"},
            {"phase": 164, "name": "Orchestration Playbooks v1", "status": "merged"},
            {"phase": 165, "name": "Pipeline Persistence + Low-Risk Executor v1", "status": "merged"},
            {"phase": 166, "name": "Execution Modes Engine v1", "status": "merged"},
            {"phase": 167, "name": "Playbook Templates Library", "status": "merged"},
            {"phase": 168, "name": "GitHub Approved Actions Executor", "status": "merged"},
            {"phase": 169, "name": "Memory Sync Runtime", "status": "merged"},
            {"phase": 170, "name": "Local Knowledge/RAG Decision v1", "status": "merged"},
            {"phase": 171, "name": "Provider Outcome Learning", "status": "merged"},
            {"phase": 172, "name": "Home/App Control Surface", "status": "merged"},
            {"phase": 173, "name": "Home Visual Shell", "status": "merged"},
            {"phase": 174, "name": "Launcher/App Default Home Route", "status": "merged"},
            {"phase": 175, "name": "Global State + README Refresh + Operating Model", "status": "merged"},
            {"phase": 176, "name": "Cockpit Runtime UX + Execution Logs", "status": "merged"},
            {"phase": 177, "name": "Project Tree Autorefresh + GOD_MODE Tree", "status": "merged"},
            {"phase": 178, "name": "Module Registry Snapshot + GOD_MODE Tree Integration", "status": "merged"},
            {"phase": 179, "name": "Reality Audit + First Real Install Mission", "status": "in_progress"},
        ]

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {
                "device": "home_pc",
                "role": "powerful_backend_runtime",
                "responsibilities": [
                    "run FastAPI backend",
                    "control local browser/tools/providers where approved",
                    "prepare repo patches and PRs",
                    "build Windows/Android artifacts",
                    "store local runtime state",
                    "host local/private vault implementation when added",
                ],
            },
            "primary_cockpit": {
                "device": "android_phone",
                "role": "remote_operator_cockpit",
                "reason": "Operator is frequently outside/driving/working and needs mobile-first command and approval.",
                "entrypoint": "/app/home",
                "responsibilities": [
                    "send commands",
                    "approve/reject gated actions",
                    "monitor what the PC brain is doing",
                    "provide temporary credentials only when unavoidable",
                    "receive status, logs and next-action prompts",
                ],
            },
            "secondary_cockpit": {
                "device": "pc_browser_or_desktop_launcher",
                "role": "local_operator_cockpit_when_at_home",
                "entrypoint": "/app/home",
            },
            "canonical_entrypoint": {
                "route": "/app/home",
                "manifest": "/api/app-entrypoint/manifest",
                "control_surface_package": "/api/home-control-surface/package",
                "runtime_ux_package": "/api/cockpit-runtime-ux/package",
                "reality_audit_package": "/api/god-mode-reality-audit/package",
            },
        }

    def project_tree_model(self) -> Dict[str, Any]:
        return {
            "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md",
            "legacy_tree_path": "PROJECT_TREE.txt",
            "project_id": "GOD_MODE",
            "generator_script": "scripts/generate_project_tree.py",
            "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml",
            "backend_package": "/api/project-tree-autorefresh/package",
            "status_endpoint": "/api/module-registry-snapshot/tree-status",
            "manual_tree_is_fallback_only": True,
        }

    def reality_audit_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/god-mode-reality-audit/package",
            "purpose": "Separate real, partial, planned and blocked capabilities before first PC install.",
            "first_install_mission_endpoint": "/api/god-mode-reality-audit/first-install-mission",
            "rule": "No capability should be presented as fully real until it passes PC/runtime proof.",
        }

    def memory_model(self) -> Dict[str, Any]:
        return {
            "github_memory": {
                "repo": "AndreVazao/andreos-memory",
                "role": "stable_technical_memory",
                "stores": ["architecture", "decisions", "history", "backlog", "latest_session", "prompts"],
                "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "customer_private_data", "runtime_secrets"],
            },
            "obsidian_local": {
                "role": "local_workshop_and_live_operational_memory",
                "stores": ["local drafts", "working notes", "operator thinking", "live progress", "local-only context"],
                "cloud_dependency": False,
            },
            "god_mode_runtime": {
                "role": "active operational state used by PC backend and cockpits",
                "stores": ["pipeline state", "button execution logs", "provider outcomes", "safe action queues", "local indexes", "module registry snapshot", "reality audit"],
            },
        }

    def vault_policy(self) -> Dict[str, Any]:
        return {
            "status": "planned_local_first_contract",
            "principle": "Secrets belong in a local encrypted PC vault, never in GitHub memory or README/docs.",
            "allowed_now": [
                "store secret references/labels",
                "store target platform mapping without secret values",
                "ask operator for temporary credential when unavoidable",
                "record that a credential was needed without recording the credential",
            ],
            "blocked": [
                "commit secrets to GitHub",
                "write passwords/tokens/cookies to AndreOS memory",
                "send secrets to external providers as context",
                "log raw credential values",
            ],
            "future_requirements": [
                "local encrypted vault on PC",
                "per-platform secret reference IDs",
                "operator mobile approval for vault unlock/use",
                "audit log with redacted secret IDs only",
                "manual override and revoke flow",
            ],
        }

    def self_update_model(self) -> Dict[str, Any]:
        return {
            "status": "roadmap_high_priority",
            "goal": "God Mode can patch itself, open PRs, validate builds and prepare updates while keeping merge/release behind gates.",
            "already_available": [
                "GitHub Approved Actions Executor can prepare branches/files/PRs",
                "GitHub Actions validates Universal, Android, Windows and smokes",
                "desktop update helper exists in Windows artifact support bundle",
                "Memory Sync Runtime records merged phases",
                "Project Tree Autorefresh keeps GOD_MODE_TREE.md current after main changes",
            ],
            "still_needed": [
                "self-update orchestrator that detects accepted God Mode changes",
                "update channel manifest for desktop/APK",
                "download/install staged update flow",
                "rollback checkpoint on PC",
                "mobile approval for upgrade apply",
                "never auto-merge/release without Oner approval",
            ],
            "gates": [
                "PR created",
                "all required GitHub Actions green",
                "operator approval",
                "release/update package prepared",
                "rollback available",
            ],
        }

    def backlog(self) -> Dict[str, Any]:
        return {
            "high_priority_next": [
                "Run first real PC install mission",
                "Install/verify Playwright and PC browser runner for AI conversations",
                "Local encrypted PC vault contract implementation",
                "Self-update orchestrator and staged update manifests",
            ],
            "medium_priority": [
                "Voice-first safe commands",
                "Advanced local RAG with embeddings/vector index",
                "Deeper mobile UI for approvals and secrets handoff",
                "More automation playbook templates",
            ],
            "always": [
                "Update AndreOS memory after merged phases",
                "Keep README aligned with real architecture",
                "Validate with GitHub Actions before merge",
                "Never store secrets in repo/docs/memory",
                "Check module registry snapshot before creating new modules",
                "Use docs/project-tree/GOD_MODE_TREE.md as the official tree artifact",
                "Mark unproven provider/browser powers as partial until PC runtime proves them",
            ],
        }

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        phases = self.implemented_phases()
        merged = [phase for phase in phases if phase["status"] == "merged"]
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "implemented_phase_count": len(merged),
            "latest_merged_phase": 178,
            "current_phase": 179,
            "canonical_cockpit_route": "/app/home",
            "mobile_first": True,
            "pc_brain": True,
            "github_memory_required_for_technical_continuity": True,
            "secrets_allowed_in_memory": False,
            "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md",
            "module_registry_endpoint": "/api/module-registry-snapshot/package",
            "reality_audit_endpoint": "/api/god-mode-reality-audit/package",
        }

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "implemented_phases": self.implemented_phases(),
            "operating_model": self.operating_model(),
            "project_tree_model": self.project_tree_model(),
            "reality_audit_model": self.reality_audit_model(),
            "module_registry": self.module_registry(),
            "memory_model": self.memory_model(),
            "vault_policy": self.vault_policy(),
            "self_update_model": self.self_update_model(),
            "backlog": self.backlog(),
        }


god_mode_global_state_service = GodModeGlobalStateService()
