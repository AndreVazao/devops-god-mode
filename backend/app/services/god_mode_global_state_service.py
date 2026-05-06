from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_201_v1"

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
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 201, "name": "Native Skills Runtime + Candidate Adoption Queue", "status": "in_progress"})
        return result

    def controlled_self_evolution_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/external-skills-lab-registry/package",
            "route": "/app/external-skills-lab-registry",
            "alias": "/app/skills-labs",
            "features": ["recognize external skills labs", "decide useful code/patterns for operator requests", "assess newly discovered repos", "prepare lab creation plan with README and import workflow template", "create reuse plan for native God Mode evolution", "create review cards"],
            "can_apply_code_without_gate": False,
            "can_create_lab_without_gate": False,
            "blocked": ["direct merge", "release", "store secrets", "blind code copy", "quarantined browser automation without gate"],
        }

    def external_lab_snapshot_reader_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/external-lab-snapshot-reader/package",
            "route": "/app/external-lab-snapshot-reader",
            "alias": "/app/lab-snapshot-reader",
            "purpose": "Read sanitized docs/UPSTREAM_SNAPSHOT.json evidence from external labs and propose native_skill_candidate plans.",
            "features": ["ingest pasted snapshot JSON from mobile cockpit", "ingest structured snapshot payloads", "generate fallback candidates from the External Skills Lab Registry", "classify candidate domain", "classify risk and required approvals", "create candidate plans with PR/gate/test steps", "create mobile review cards"],
            "can_apply_candidate_without_gate": False,
            "can_import_raw_lab_code_without_review": False,
        }

    def native_skills_adoption_queue_model(self) -> Dict[str, Any]:
        return {
            "endpoint": "/api/native-skills-adoption-queue/package",
            "route": "/app/native-skills-adoption-queue",
            "alias": "/app/native-skills-runtime",
            "purpose": "Promote native_skill_candidate records into an adoption queue and prepare gated implementation plans without applying code directly.",
            "statuses": ["proposed", "needs_review", "approved_for_planning", "planned", "rejected", "quarantined"],
            "features": ["promote candidate", "promote by domain/risk filter", "update controlled status", "create implementation plan", "reuse-first module registry evidence", "create mobile review cards", "decision log"],
            "can_apply_code_without_gate": False,
            "can_merge_without_oner_approval": False,
        }

    def operating_model(self) -> Dict[str, Any]:
        return {
            "primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["evaluate labs", "read lab snapshots", "promote candidates into adoption queue", "plan controlled self-evolution", "prepare gated PR plans"]},
            "primary_cockpit": {"device": "android_phone", "role": "remote_operator_cockpit", "entrypoint": "/app/home", "responsibilities": ["ask for evolution", "paste lab snapshots", "review candidates", "approve planning", "approve risky gates"]},
            "canonical_entrypoint": {"route": "/app/home", "skills_labs_route": "/app/external-skills-lab-registry", "lab_snapshot_reader_route": "/app/external-lab-snapshot-reader", "native_skills_adoption_queue_route": "/app/native-skills-adoption-queue"},
        }

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
        return {"endpoint": "/api/real-work-fast-path/package", "route": "/app/real-work-fast-path", "default_groups": ["god_mode", "baribudos_platform", "proventil"]}

    def project_tree_model(self) -> Dict[str, Any]:
        return {"official_tree_path": "docs/project-tree/GOD_MODE_TREE.md", "project_id": "GOD_MODE", "autorefresh_workflow": ".github/workflows/project-tree-autorefresh.yml"}

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "god_mode_runtime": {"stores": ["external lab registry", "lab snapshot imports", "native skill candidates", "native skills adoption queue", "implementation plans", "candidate plans", "controlled evolution cards"]}}

    def reality_policy(self) -> Dict[str, Any]:
        return {"status": "phase_201_native_skills_adoption_queue", "principle": "God Mode can promote native skill candidates into a controlled adoption queue and plan implementations, but code application, merges, releases and risky automations remain gated.", "blocked": ["merge without approval", "release without approval", "store secrets", "blind external code copy", "apply candidate code without PR"], "required": ["candidate evidence", "adoption queue item", "controlled status", "implementation plan", "PR flow", "green checks", "AndreOS memory update"]}

    def backlog(self) -> Dict[str, Any]:
        return {"high_priority_next": ["Candidate-to-PR Plan Generator", "Provider Automation Gates v1", "Self-update install path", "Lab snapshot fetch via GitHub connector when approved"], "always": ["Update AndreOS memory after merged phases", "Never store raw secrets", "Use GOD_MODE_TREE.md as official tree artifact", "Delete old phase smoke workflows when advancing"]}

    def module_registry(self) -> Dict[str, Any]:
        return module_registry_snapshot_service.package()

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "latest_merged_phase": 200, "current_phase": 201, "canonical_cockpit_route": "/app/home", "skills_labs_route": "/app/external-skills-lab-registry", "lab_snapshot_reader_route": "/app/external-lab-snapshot-reader", "native_skills_adoption_queue_route": "/app/native-skills-adoption-queue", "mobile_first": True, "pc_brain": True, "secrets_allowed_in_memory": False, "official_tree_path": "docs/project-tree/GOD_MODE_TREE.md"}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "project_tree_model": self.project_tree_model(), "real_work_fast_path_model": self.real_work_fast_path_model(), "repo_scanner_real_work_map_model": self.repo_scanner_real_work_map_model(), "github_repo_inventory_feed_model": self.github_repo_inventory_feed_model(), "conversation_source_import_feed_model": self.conversation_source_import_feed_model(), "provider_browser_local_launcher_model": self.provider_browser_local_launcher_model(), "first_pc_runtime_verification_model": self.first_pc_runtime_verification_model(), "controlled_self_evolution_model": self.controlled_self_evolution_model(), "external_lab_snapshot_reader_model": self.external_lab_snapshot_reader_model(), "native_skills_adoption_queue_model": self.native_skills_adoption_queue_model(), "module_registry": self.module_registry(), "memory_model": self.memory_model(), "reality_policy": self.reality_policy(), "backlog": self.backlog()}


god_mode_global_state_service = GodModeGlobalStateService()
