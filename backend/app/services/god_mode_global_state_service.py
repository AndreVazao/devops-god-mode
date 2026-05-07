from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_206_v1"

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
            (195, "GitHub Repo Inventory Connector + Real Work Scanner Feed"), (196, "Conversation Source Import Automation + Work Map Feed"),
            (197, "Provider Browser Proof Local Launcher + Capture Contract"), (198, "First PC Install Operator Guide + Runtime Verification Cockpit"),
            (199, "Controlled Self-Evolution + External Skills Lab Registry"), (200, "External Lab Snapshot Reader + Native Skill Candidate Planner"),
            (201, "Native Skills Runtime + Candidate Adoption Queue"), (202, "First PC Install Ready Pack + One-Click Local Start Contract"),
            (203, "God Mode Self-Diagnosis Mission Control + Fix-What-Is-Missing Queue"),
            (204, "Autonomous IA Work Session Operator + Provider Work Pack Queue"),
            (205, "Mobile Permission Relay + Driver Voice Mode + Offline Resend Queue + Local Vault Intake"),
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 206, "name": "IA Operator Permission/Vault Bridge + First Autonomous Work Loop", "status": "in_progress"})
        return result

    def ia_operator_bridge_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/ia-operator-bridge/package", "route": "/app/ia-operator-bridge", "alias": "/app/first-autonomous-work-loop", "purpose": "Run first safe autonomous loop: self-diagnosis, IA work packets, vault reference binding, mobile permission if needed, response import and task conversion.", "can_start_first_autonomous_work_loop": True, "can_use_vault_references": True, "can_request_mobile_permission": True, "can_apply_code_without_pr": False, "can_merge_without_oner_approval": False}

    def mobile_permission_relay_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/mobile-permission-relay/package", "route": "/app/mobile-permission-relay", "alias": "/app/driver-voice-permissions", "can_resend_after_offline": True, "supports_driver_voice_mode": True, "can_store_sensitive_values_in_local_vault": True}

    def god_mode_local_vault_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/god-mode-vault/status", "route": "/app/god-mode-vault", "alias": "/app/vault-intake", "intake_endpoint": "/api/god-mode-vault/intake-text", "references_endpoint": "/api/god-mode-vault/references", "stores_encrypted_values_locally": True, "stores_raw_values_in_repo_or_normal_memory": False}

    def autonomous_ia_work_session_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/autonomous-ia-work-session/package", "route": "/app/autonomous-ia-work-session", "alias": "/app/ia-work-operator", "can_operate_while_oner_busy": True}

    def first_pc_install_ready_pack_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/first-pc-install-ready-pack/package", "route": "/app/first-pc-install-ready-pack", "alias": "/app/pc-install-ready", "canonical_local_url": "http://127.0.0.1:8000/app/home", "expected_executable": "GodModeDesktop.exe"}

    def god_mode_self_diagnosis_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/god-mode-self-diagnosis/package", "route": "/app/god-mode-self-diagnosis", "alias": "/app/self-fix-mission-control"}

    def operating_model(self) -> Dict[str, Any]:
        return {"primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["run GodModeDesktop.exe", "serve backend locally", "start safe autonomous loop", "wait for mobile permissions", "reuse vault references"]}, "primary_cockpit": {"device": "android_phone", "role": "popup_voice_permission_cockpit", "entrypoint": "/app/mobile-permission-relay"}, "pc_cockpit": {"device": "home_pc_browser", "entrypoint": "/app/first-pc-install-ready-pack", "first_loop": "/app/ia-operator-bridge", "local_url": "http://127.0.0.1:8000/app/home"}}

    def controlled_self_evolution_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/external-skills-lab-registry/package", "route": "/app/external-skills-lab-registry", "alias": "/app/skills-labs"}

    def external_lab_snapshot_reader_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/external-lab-snapshot-reader/package", "route": "/app/external-lab-snapshot-reader", "alias": "/app/lab-snapshot-reader"}

    def native_skills_adoption_queue_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/native-skills-adoption-queue/package", "route": "/app/native-skills-adoption-queue", "alias": "/app/native-skills-runtime"}

    def first_pc_runtime_verification_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/first-pc-runtime-verification/package", "route": "/app/first-pc-runtime-verification"}

    def provider_browser_local_launcher_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/provider-browser-local-launcher/package", "route": "/app/provider-browser-local-launcher", "executes_browser_automation": False}

    def conversation_source_import_feed_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/conversation-source-import-feed/package", "route": "/app/conversation-source-import-feed"}

    def github_repo_inventory_feed_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/github-repo-inventory-feed/package", "route": "/app/github-repo-inventory-feed"}

    def repo_scanner_real_work_map_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/repo-scanner-real-work-map/package", "route": "/app/repo-scanner-real-work-map"}

    def real_work_fast_path_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/real-work-fast-path/package", "route": "/app/real-work-fast-path"}

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "project_id": "GOD_MODE"}

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "god_mode_runtime": {"stores": ["first autonomous work loop", "bridge events", "packet bindings", "local encrypted vault", "mobile permission relay"]}}

    def reality_policy(self) -> Dict[str, Any]:
        return {"status": "phase_206_ia_operator_permission_vault_bridge", "principle": "God Mode can start the first safe autonomous loop and bind IA packets to vault references or mobile permission requests, but code application and final gates remain human-approved.", "blocked_runtime_autonomy": ["apply patches without PR", "merge/release/deploy without approval", "private provider login automation"], "required": ["autonomous loop", "packet binding", "vault reference or permission request", "response import", "task conversion"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Installable first-run autopilot page", "PC artifact direct download final guide", "Bridge task to PR plan generator", "Mobile push transport adapter"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets in repo", "Delete old phase smoke workflows when advancing"]}

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "latest_merged_phase": 205, "current_phase": 206, "canonical_cockpit_route": "/app/home", "ia_operator_bridge_route": "/app/ia-operator-bridge", "mobile_first": True, "pc_brain": True, "secrets_allowed_in_memory": False, "secrets_allowed_in_local_encrypted_vault": True}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "real_work_fast_path_model": self.real_work_fast_path_model(), "repo_scanner_real_work_map_model": self.repo_scanner_real_work_map_model(), "github_repo_inventory_feed_model": self.github_repo_inventory_feed_model(), "conversation_source_import_feed_model": self.conversation_source_import_feed_model(), "provider_browser_local_launcher_model": self.provider_browser_local_launcher_model(), "first_pc_runtime_verification_model": self.first_pc_runtime_verification_model(), "first_pc_install_ready_pack_model": self.first_pc_install_ready_pack_model(), "god_mode_self_diagnosis_model": self.god_mode_self_diagnosis_model(), "autonomous_ia_work_session_model": self.autonomous_ia_work_session_model(), "mobile_permission_relay_model": self.mobile_permission_relay_model(), "god_mode_local_vault_model": self.god_mode_local_vault_model(), "ia_operator_bridge_model": self.ia_operator_bridge_model(), "controlled_self_evolution_model": self.controlled_self_evolution_model(), "external_lab_snapshot_reader_model": self.external_lab_snapshot_reader_model(), "native_skills_adoption_queue_model": self.native_skills_adoption_queue_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "reality_policy": self.reality_policy(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
