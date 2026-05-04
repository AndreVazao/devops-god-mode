from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.module_registry_snapshot_service import module_registry_snapshot_service
from app.services.external_ai_browser_worker_service import external_ai_browser_worker_service
from app.services.external_ai_chat_reader_service import external_ai_chat_reader_service
from app.services.multi_ai_conversation_inventory_service import multi_ai_conversation_inventory_service
from app.services.project_tree_autorefresh_service import project_tree_autorefresh_service
from app.services.god_mode_global_state_service import god_mode_global_state_service


class GodModeRealityAuditService:
    """Honest real-vs-superficial capability audit.

    The goal is to avoid selling fantasy. Each capability is marked as:
    - real: already implemented and locally callable in backend/CI.
    - partial: contracts/services exist but need PC runtime/operator setup.
    - planned: documented but not real execution yet.
    - blocked: cannot run until dependency/setup is completed.
    """

    SERVICE_ID = "god_mode_reality_audit"
    VERSION = "phase_179_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        audit = self.audit()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "overall_real_percent": audit["overall"]["real_percent"],
            "overall_label": audit["overall"]["label"],
            "fantasy_risk": audit["overall"]["fantasy_risk"],
            "first_install_ready": audit["first_install_mission"]["ready_for_pc_install_attempt"],
        }

    def audit(self) -> Dict[str, Any]:
        capabilities = self.capabilities()
        counts = self._counts(capabilities)
        real_percent = round((counts["real"] + counts["partial"] * 0.45) * 100 / max(counts["total"], 1))
        fantasy_risk = "medium" if counts["partial"] or counts["planned"] else "low"
        if counts["blocked"]:
            fantasy_risk = "high"
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "overall": {
                "real_percent": real_percent,
                "label": self._label(real_percent),
                "fantasy_risk": fantasy_risk,
                "counts": counts,
                "honest_note": "Backend/builds are real; browser/provider conversation execution is partial until PC runner + Playwright + manual login are proven on the real PC.",
            },
            "capabilities": capabilities,
            "first_install_mission": self.first_install_mission(),
            "project_tree_and_inventory_mission": self.project_tree_and_inventory_mission(),
            "hard_truths": self.hard_truths(capabilities),
        }

    def capabilities(self) -> List[Dict[str, Any]]:
        playwright_available = importlib.util.find_spec("playwright") is not None
        tree_status = project_tree_autorefresh_service.get_status()
        module_status = module_registry_snapshot_service.status()
        browser_cap = external_ai_browser_worker_service.capability_report()
        reader_cap = external_ai_chat_reader_service.capability_report()
        inventory_status = multi_ai_conversation_inventory_service.get_status()
        global_state = god_mode_global_state_service.status()
        return [
            self._cap("backend_api", "Backend FastAPI/routes", "real", "Routes auto-load and smoke tests validate import/runtime.", evidence={"global_state_ok": global_state.get("ok"), "route_modules": module_status.get("route_module_count")}),
            self._cap("windows_exe_build", "Windows EXE build", "real", "Windows build and boot smoke pass in GitHub Actions.", evidence={"validated_by": "Windows EXE Build + boot smoke"}),
            self._cap("android_apk_build", "Android APK build", "real", "Android WebView APK build passes in GitHub Actions.", evidence={"validated_by": "Android APK Build"}),
            self._cap("mobile_pc_cockpit_contract", "Phone cockpit + PC brain contract", "real", "Cockpit routes/packages exist; real LAN pairing still must be tested on PC/phone.", evidence={"route": "/app/home", "runtime_package": "/api/cockpit-runtime-ux/package"}),
            self._cap("operator_logs", "Button logs/history", "real", "Cockpit Runtime UX writes to Operator Action Journal.", evidence={"endpoint": "/api/cockpit-runtime-ux/log-button-event"}),
            self._cap("project_tree_autorefresh", "Official GOD_MODE tree", "real", "Generator/workflow/backend service exist; workflow auto-commit needs next main push proof.", evidence={"tree_status": tree_status}),
            self._cap("module_registry", "Module registry snapshot", "real", "Routes/services are categorized by filename and searchable.", evidence={"routes": module_status.get("route_module_count"), "services": module_status.get("service_module_count")}),
            self._cap("conversation_inventory_manual", "Multi-AI conversation inventory by manual/staged input", "real", "Inventory can store staged conversations and map projects/providers.", evidence={"inventory_status": inventory_status.get("status")}),
            self._cap("external_ai_browser_worker", "External AI browser worker", "partial" if playwright_available else "blocked", "Contracts and probes exist; actual browser control requires Playwright and real PC runner/session.", evidence={"playwright_available": playwright_available, "browser_status": browser_cap.get("status")}),
            self._cap("external_ai_chat_reader", "External AI chat visible reader", "partial" if playwright_available else "blocked", "Reader plans/selectors/snapshot normalization exist; actual read must run on PC browser context after manual login.", evidence={"playwright_available": playwright_available, "reader_status": reader_cap.get("status")}),
            self._cap("provider_login_persistence", "Provider login/session persistence", "partial", "Manual login flow exists as contract; durable local session/vault strategy still needs real PC hardening.", evidence={"stores_credentials": False, "manual_login_required": True}),
            self._cap("vault", "Local encrypted vault", "planned", "Policy/placeholder modules exist; real encrypted vault flow is next critical phase.", evidence={"next_phase": "Local Encrypted Vault Contract"}),
            self._cap("self_update", "God Mode self-update", "partial", "Build/update helpers and GitHub patch executor exist; staged update + rollback orchestration still pending.", evidence={"requires": ["manifest", "staging", "rollback", "mobile approval"]}),
            self._cap("real_project_execution", "First real project continuation", "partial", "Repo patch/build pieces exist; first PC install + real project run must prove end-to-end power.", evidence={"requires": ["install", "provider login", "conversation inventory", "tree scan", "approved patch"]}),
        ]

    def first_install_mission(self) -> Dict[str, Any]:
        return {
            "ready_for_pc_install_attempt": True,
            "mission_name": "first_real_pc_install_and_power_check",
            "goal": "Install on PC, open /app/home, connect phone, inventory conversations, scan project trees, and prove what is real.",
            "steps": [
                {"id": 1, "label": "Download latest Windows artifact and run backend/launcher", "proof": "health endpoint and /app/home load"},
                {"id": 2, "label": "Open phone cockpit to PC LAN URL", "proof": "phone loads /app/home and /api/cockpit-runtime-ux/package"},
                {"id": 3, "label": "Run module registry snapshot", "proof": "/api/module-registry-snapshot/summary returns counts"},
                {"id": 4, "label": "Run tree status/autorefresh", "proof": "GOD_MODE_TREE.md exists or workflow/manual dispatch creates it"},
                {"id": 5, "label": "Stage/list AI conversations manually first", "proof": "/api/multi-ai-conversation-inventory package shows conversations"},
                {"id": 6, "label": "Install/verify Playwright on PC if external browser automation is desired", "proof": "external AI browser worker reports browser_worker_available"},
                {"id": 7, "label": "Manual login to selected providers", "proof": "operator confirms login; no credentials are stored"},
                {"id": 8, "label": "Read visible conversation snapshot", "proof": "external chat reader returns normalized snapshot"},
                {"id": 9, "label": "Generate project tree for a chosen repo/conversation", "proof": "named tree artifact exists"},
                {"id": 10, "label": "Do one approved low-risk repo/file action", "proof": "preview/PR/checks or local write with rollback"},
            ],
        }

    def project_tree_and_inventory_mission(self) -> Dict[str, Any]:
        return {
            "first_priority": "Map conversations to projects and trees before doing code work.",
            "inputs": ["conversation title/snippet/url/provider", "repo path/name", "expected project tree from chat", "real project tree from repo"],
            "outputs": ["conversation inventory", "project map", "GOD_MODE_TREE.md or per-project tree", "reuse-first decision"],
            "rule": "If a chat contains an expected tree and repo contains real tree, store both and prefer real tree for code operations while keeping expected tree as design intent.",
        }

    def hard_truths(self, capabilities: List[Dict[str, Any]]) -> List[str]:
        return [
            "The backend is not just fantasy: many routes/services build and pass CI.",
            "But external AI conversation listing/reading is not fully proven until it runs on the real PC browser session.",
            "Without Playwright or a local runner, the system can plan and normalize snapshots, not truly browse providers.",
            "Vault must be implemented before trusting repeated provider/deploy credential flows.",
            "The first real PC install is now the deciding test: health, phone cockpit, provider login, conversation inventory, tree scan, then one approved action.",
        ]

    def _cap(self, capability_id: str, label: str, status: str, assessment: str, evidence: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {"id": capability_id, "label": label, "status": status, "assessment": assessment, "evidence": evidence or {}}

    def _counts(self, capabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        counts = {"real": 0, "partial": 0, "planned": 0, "blocked": 0, "total": len(capabilities)}
        for cap in capabilities:
            counts[cap.get("status", "planned")] = counts.get(cap.get("status", "planned"), 0) + 1
        return counts

    def _label(self, percent: int) -> str:
        if percent >= 85:
            return "strong_real_core_needs_pc_proof"
        if percent >= 70:
            return "advanced_but_not_fully_proven"
        if percent >= 50:
            return "mixed_real_and_superficial"
        return "too_superficial"

    def package(self) -> Dict[str, Any]:
        return {"status": self.status(), "audit": self.audit()}


god_mode_reality_audit_service = GodModeRealityAuditService()
