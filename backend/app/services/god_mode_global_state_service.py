from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service


class GodModeGlobalStateService:
    SERVICE_ID = "god_mode_global_state"
    VERSION = "phase_210_v1"

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
            (206, "IA Operator Permission/Vault Bridge + First Autonomous Work Loop"),
            (207, "First PC Autopilot Install/Run Cockpit + Today Ready Flow"),
            (208, "Mobile APK to PC Pairing + Remote Access Contract"),
            (209, "LAN Connection Discovery Sweep"),
        ]
        result = [{"phase": phase, "name": name, "status": "merged"} for phase, name in phases]
        result.append({"phase": 210, "name": "Final Install & Use Pack + APK Auto Endpoint Contract", "status": "in_progress"})
        return result

    def final_install_use_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/final-install-use/package", "route": "/app/install-use-now", "alias": "/app/final-ready", "purpose": "Final page to install Windows EXE, install APK, connect phone, verify readiness and start God Mode real usage.", "ready_to_install_and_use": True, "apk_endpoint_contract": "/api/final-install-use/apk-endpoint-contract"}

    def mobile_pc_pairing_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/mobile-pc-pairing/package", "route": "/app/mobile-pc-pairing", "alias": "/app/connect-phone", "lan_sweep": "192.168.1.61-192.168.1.101", "known_pc": "192.168.1.81", "known_phone_hint": "192.168.1.47"}

    def today_ready_model(self) -> Dict[str, Any]:
        return {"endpoint": "/api/first-pc-autopilot-ready/package", "route": "/app/first-pc-autopilot-ready", "alias": "/app/today-ready", "canonical_local_url": "http://127.0.0.1:8000/app/home", "expected_executable": "GodModeDesktop.exe", "first_loop_route": "/app/ia-operator-bridge", "phone_pairing_route": "/app/mobile-pc-pairing"}

    def operating_model(self) -> Dict[str, Any]:
        return {"primary_brain": {"device": "home_pc", "role": "powerful_backend_runtime", "responsibilities": ["run GodModeDesktop.exe", "open install-use-now", "connect APK", "start real usage", "wait for mobile permissions", "reuse vault references"]}, "primary_cockpit": {"device": "android_phone", "role": "mobile apk cockpit", "entrypoint": "/app/mobile-permission-relay", "connection_modes": ["last_working_endpoint", "home_lan_sweep", "remote_https"]}, "pc_cockpit": {"device": "home_pc_browser", "entrypoint": "/app/install-use-now", "local_url": "http://127.0.0.1:8000/app/home"}}

    def memory_model(self) -> Dict[str, Any]:
        return {"github_memory": {"repo": "AndreVazao/andreos-memory", "must_not_store": ["tokens", "passwords", "cookies", "api_keys", "raw env values"]}, "god_mode_runtime": {"stores": ["final install use readiness", "apk endpoint contract", "last working endpoint on APK", "local encrypted vault", "mobile permission relay"]}}

    def reality_policy(self) -> Dict[str, Any]:
        return {"status": "phase_210_final_install_use_ready", "principle": "God Mode is ready for first real install and use through a final cockpit, Windows EXE, Android APK, LAN sweep, remote contract, vault and autopilot start.", "blocked_runtime_autonomy": ["open router ports blindly", "publish unsafe HTTP endpoint to internet", "store sensitive material in repo", "merge/release/deploy without approval"], "required": ["install-use-now", "Windows EXE", "Android APK", "connection manifest", "vault", "start autopilot"]}

    def status(self) -> Dict[str, Any]:
        return {"ok": True, "service": self.SERVICE_ID, "version": self.VERSION, "generated_at": self._now(), "latest_merged_phase": 209, "current_phase": 210, "canonical_cockpit_route": "/app/home", "final_ready_route": "/app/install-use-now", "mobile_first": True, "pc_brain": True}

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "implemented_phases": self.implemented_phases(), "operating_model": self.operating_model(), "final_install_use_model": self.final_install_use_model(), "mobile_pc_pairing_model": self.mobile_pc_pairing_model(), "today_ready_model": self.today_ready_model(), "module_registry": module_registry_snapshot_service.package(), "memory_model": self.memory_model(), "reality_policy": self.reality_policy()}


god_mode_global_state_service = GodModeGlobalStateService()
