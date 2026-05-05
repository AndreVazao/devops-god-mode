from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    """Stable project snapshot and operating model for God Mode."""

    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_185_v1"

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
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 185, "name": "Vault Deployment Binding + Provider Env Injection Plan", "status": "in_progress"})
        return result

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["run FastAPI backend", "control local browser/tools/providers where approved", "prepare repo patches and PRs", "build Windows/Android artifacts", "store local runtime state", "host local/private encrypted vault", "prepare provider env injection plans"]},
            "primary_cockpit": {"device": "android_phone", "role": "remote_operator_cockpit", "entrypoint": "/app/home", "responsibilities": ["send commands", "approve/reject gated actions", "monitor PC brain", "approve vault/credential use", "approve env injection previews", "receive status and logs"]},
            "secondary_cockpit": {"device": "pc_browser_or_desktop_launcher", "role": "local_operator_cockpit_when_at_home", "entrypoint": "/app/home"},
            "canonical_entrypoint": {"route": "/app/home", "manifest": "/api/app-entrypoint/manifest", "real_local_encrypted_vault_package": "/api/real-local-encrypted-vault/package", "vault_deployment_binding_package": "/api/vault-deployment-binding/package"},
        }

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "legacy_tree_path": "PROJECT_TREE.txt", "project_id": "GOD_MODE", "generator_script": "scripts/generate_project_tree.py", "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml", "backend_package": "/api/project-tree-autorefresh/package", "manual_tree_is_fallback_only": True}

    def local_vault_contract_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/local-encrypted-vault-contract/package", "intake_endpoint": "/api/local-encrypted-vault-contract/intake-env-text", "stores_secret_values": False, "barbudo_mapping_note": "Barbudo Studio controls Website through API/routes/env bindings; God Mode should remember placement without exposing values."}

    def real_local_encrypted_vault_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/real-local-encrypted-vault/package", "stores_encrypted_values": True, "stores_plaintext_values": False, "passphrase_persisted": False, "approval_required_for_read_write": True}

    def vault_deployment_binding_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/vault-deployment-binding/package",
            "create_binding_endpoint": "/api/vault-deployment-binding/create-binding",
            "build_plan_endpoint": "/api/vault-deployment-binding/build-injection-plan",
            "create_apply_gate_endpoint": "/api/vault-deployment-binding/create-apply-gate",
            "apply_preview_endpoint": "/api/vault-deployment-binding/apply-preview",
            "uses_secret_ref_id_only": True,
            "remote_write_executed_in_phase": False,
            "approval_required_for_apply_preview": True,
            "supported_provider_modes": ["vercel_env", "render_env", "supabase_config", "github_actions_secret", "local_process_env", "manual_export"],
        }

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "role": "stable_technical_memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "obsidian_local": {"role": "local workshop; may mirror safe labels/notes, never cloud-sync raw secrets"}, "god_mode_runtime": {"role": "active operational state", "stores": ["vault references", "encrypted vault index", "deployment binding plans", "redacted apply previews"]}}

    def vault_policy(self) -> Dict[str, Any]:
        return {"status": "phase_185_binding_plans", "principle": "Deploy/env/provider plans use secret_ref_id only. Secret values are decrypted only locally after approval for immediate injection/preview.", "allowed_now": ["local encrypted value store", "secret_ref bindings", "provider/project/environment mapping", "redacted apply previews"], "blocked": ["commit raw values", "remote provider write without explicit future gate", "log raw values", "persist passphrase"], "future_requirements": ["provider-specific writers", "Windows DPAPI/OS keyring", "rotation"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Run first real PC install mission", "Wire provider-specific env writers after manual proof", "Self-update orchestrator and staged update manifests"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets in repo/docs/memory", "Check module registry before new modules", "Use GOD_MODE_TREE.md as official tree artifact", "Delete old phase smoke workflows when advancing"]}

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "implemented_phase_count": 30, "latest_merged_phase": 184, "current_phase": 185, "canonical_cockpit_route": "/app/home", "mobile_first": True, "pc_brain": True, "secrets_allowed_in_memory": False, "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "real_local_encrypted_vault_endpoint": "/api/real-local-encrypted-vault/package", "vault_deployment_binding_endpoint": "/api/vault-deployment-binding/package"}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "local_vault_contract_model": self.local_vault_contract_model(), "real_local_encrypted_vault_model": self.real_local_encrypted_vault_model(), "vault_deployment_binding_model": self.vault_deployment_binding_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "vault_policy": self.vault_policy(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
