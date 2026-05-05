from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    """Stable project snapshot and operating model for God Mode."""

    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_182_v1"

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
            {"phase": 179, "name": "Reality Audit + First Real Install Mission", "status": "merged"},
            {"phase": 180, "name": "PC Runner + Provider Conversation Proof", "status": "merged"},
            {"phase": 181, "name": "First Install Download Center + PC Proof Checklist UI", "status": "merged"},
            {"phase": 182, "name": "Local Encrypted Vault Contract + First Credential Flow", "status": "in_progress"},
        ]

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["run FastAPI backend", "control local browser/tools/providers where approved", "prepare repo patches and PRs", "build Windows/Android artifacts", "store local runtime state", "host local/private vault implementation when added"]},
            "primary_cockpit": {"device": "android_phone", "role": "remote_operator_cockpit", "entrypoint": "/app/home", "responsibilities": ["send commands", "approve/reject gated actions", "monitor PC brain", "approve vault/credential use", "receive status and logs"]},
            "secondary_cockpit": {"device": "pc_browser_or_desktop_launcher", "role": "local_operator_cockpit_when_at_home", "entrypoint": "/app/home"},
            "canonical_entrypoint": {"route": "/app/home", "manifest": "/api/app-entrypoint/manifest", "control_surface_package": "/api/home-control-surface/package", "runtime_ux_package": "/api/cockpit-runtime-ux/package", "reality_audit_package": "/api/god-mode-reality-audit/package", "pc_provider_proof_package": "/api/pc-provider-conversation-proof/package", "first_install_pc_proof_page": "/api/first-install-pc-proof-center/app", "local_vault_contract_package": "/api/local-encrypted-vault-contract/package"},
        }

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "legacy_tree_path": "PROJECT_TREE.txt", "project_id": "GOD_MODE", "generator_script": "scripts/generate_project_tree.py", "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml", "backend_package": "/api/project-tree-autorefresh/package", "manual_tree_is_fallback_only": True}

    def reality_audit_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/god-mode-reality-audit/package", "first_install_mission_endpoint": "/api/god-mode-reality-audit/first-install-mission", "rule": "No capability should be presented as fully real until it passes PC/runtime proof."}

    def pc_provider_proof_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/pc-provider-conversation-proof/package", "probe_tool": "tools/pc_provider_conversation_probe.py", "proof_dir": "data/provider_proofs", "supported_providers": ["chatgpt", "claude", "gemini", "perplexity"], "goal": "Prove provider browser/session/conversation reading on the real PC without storing credentials."}

    def first_install_pc_proof_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/first-install-pc-proof-center/package", "page": "/api/first-install-pc-proof-center/app", "operator_priority": "critical_for_first_install"}

    def local_vault_contract_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/local-encrypted-vault-contract/package",
            "intake_endpoint": "/api/local-encrypted-vault-contract/intake-env-text",
            "project_mapping_endpoint": "/api/local-encrypted-vault-contract/bootstrap-project-mapping",
            "stores_secret_values": False,
            "stores_only": ["secret_ref_id", "fingerprint", "provider_guess", "project_guess", "environment_name", "placement_plan"],
            "barbudo_mapping_note": "Barbudo Studio controls Website through API/routes/env bindings; God Mode should remember placement without exposing values.",
            "example_vs_real_rule": "example/demo/sample values are classified as example_value and must not be deployed.",
        }

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "role": "stable_technical_memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "obsidian_local": {"role": "local workshop; may mirror safe labels/notes, never cloud-sync raw secrets"}, "god_mode_runtime": {"role": "active operational state", "stores": ["pipeline state", "provider proof imports", "first install checklist", "vault references", "placement plans"]}}

    def vault_policy(self) -> Dict[str, Any]:
        return {"status": "phase_182_contract", "principle": "God Mode may know where a secret belongs, but not expose/store its raw value in GitHub/docs/memory/logs.", "allowed_now": ["secret references", "provider/project/environment mapping", "fingerprints", "placement plans", "example-vs-real classification"], "blocked": ["commit raw values", "send raw values to external AI", "deploy secret without approval", "log raw values"], "future_requirements": ["real local encrypted PC value store", "mobile approval for unlock/use", "redacted audit log"]}

    def self_update_model(self) -> Dict[str, Any]:
        return {"status": "roadmap_high_priority", "already_available": ["GitHub patch executor", "CI validation", "first install proof center", "local vault contract"], "still_needed": ["staged update manifest", "rollback checkpoint", "mobile approval for apply"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Run first real PC install mission", "Use local vault contract to classify uploaded env files", "Implement real local encrypted value store", "Self-update orchestrator and staged update manifests"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets in repo/docs/memory", "Check module registry before new modules", "Use GOD_MODE_TREE.md as official tree artifact"]}

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
            "latest_merged_phase": 181,
            "current_phase": 182,
            "canonical_cockpit_route": "/app/home",
            "mobile_first": True,
            "pc_brain": True,
            "secrets_allowed_in_memory": False,
            "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md",
            "module_registry_endpoint": "/api/module-registry-snapshot/package",
            "reality_audit_endpoint": "/api/god-mode-reality-audit/package",
            "pc_provider_proof_endpoint": "/api/pc-provider-conversation-proof/package",
            "first_install_pc_proof_endpoint": "/api/first-install-pc-proof-center/package",
            "first_install_pc_proof_page": "/api/first-install-pc-proof-center/app",
            "local_vault_contract_endpoint": "/api/local-encrypted-vault-contract/package",
        }

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "reality_audit_model": self.reality_audit_model(), "pc_provider_proof_model": self.pc_provider_proof_model(), "first_install_pc_proof_model": self.first_install_pc_proof_model(), "local_vault_contract_model": self.local_vault_contract_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "vault_policy": self.vault_policy(), "self_update_model": self.self_update_model(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
