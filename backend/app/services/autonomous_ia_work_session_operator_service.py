from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.conversation_source_import_feed_service import conversation_source_import_feed_service
from app.services.god_mode_self_diagnosis_mission_control_service import god_mode_self_diagnosis_mission_control_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.provider_browser_local_launcher_service import provider_browser_local_launcher_service
from app.services.real_work_fast_path_service import real_work_fast_path_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
IA_WORK_SESSION_FILE = DATA_DIR / "autonomous_ia_work_session_operator.json"
IA_WORK_SESSION_STORE = AtomicJsonStore(
    IA_WORK_SESSION_FILE,
    default_factory=lambda: {"version": 1, "work_sessions": [], "work_packets": [], "response_imports": [], "review_cards": [], "decision_log": []},
)

WORK_PACKET_STATUSES = {
    "drafted",
    "ready_to_send",
    "waiting_response",
    "response_imported",
    "converted_to_tasks",
    "blocked_needs_oner",
    "cancelled",
}

SAFE_PROVIDERS = ["chatgpt", "claude", "gemini", "praison", "ruflo", "manual_ai"]


class AutonomousIaWorkSessionOperatorService:
    SERVICE_ID = "autonomous_ia_work_session_operator"
    VERSION = "phase_204_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = IA_WORK_SESSION_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(IA_WORK_SESSION_FILE),
            "work_session_count": len(state.get("work_sessions", [])),
            "work_packet_count": len(state.get("work_packets", [])),
            "response_import_count": len(state.get("response_imports", [])),
            "can_operate_while_oner_busy": True,
            "can_send_without_manual_provider_gate": False,
            "can_login_or_scrape_private_chats": False,
            "can_merge_without_oner_approval": False,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "God Mode can prepare IA work packets, prompts and response imports while Oner is busy, but risky actions and final code changes remain gated.",
                "allowed": [
                    "create work sessions for God Mode and other projects",
                    "draft provider-specific prompts/work packets",
                    "mark packets ready for manual send/capture",
                    "import IA responses pasted or captured manually",
                    "convert responses into self-fix queue or project task inputs",
                    "create approval cards only for blockers/risky decisions",
                ],
                "blocked": [
                    "drive-time interaction demand",
                    "private browser login automation",
                    "scrape private chats without explicit gate",
                    "store tokens/passwords/cookies/API keys",
                    "send prompts to paid APIs without Oner approval",
                    "merge/release/deploy without checks and Oner approval",
                ],
                "statuses": sorted(WORK_PACKET_STATUSES),
                "safe_providers": SAFE_PROVIDERS,
            },
        }

    def create_session(
        self,
        title: str,
        goal: str,
        project_id: str = "GOD_MODE",
        operator_mode: str = "oner_busy_safe",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        classification = real_work_fast_path_service.classify_text(f"{project_id} {title} {goal}")
        session = {
            "work_session_id": f"ia-work-session-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "updated_at": self._now(),
            "tenant_id": tenant_id,
            "title": title[:220],
            "goal": self._sanitize(goal)[:2000],
            "project_id": project_id[:120],
            "operator_mode": operator_mode,
            "project_group_id": classification.get("project_group_id"),
            "front": classification.get("front"),
            "status": "active",
            "rules": {
                "oner_busy_safe": operator_mode == "oner_busy_safe",
                "do_not_require_driver_interaction": True,
                "manual_provider_send_required": True,
                "no_private_login_automation": True,
                "no_secrets": True,
            },
        }
        self._store("work_sessions", session)
        card = self._create_session_card(session, tenant_id)
        return {"ok": True, "mode": "create_ia_work_session", "work_session": session, "review_card": card}

    def create_work_packet(
        self,
        work_session_id: str,
        provider: str,
        task_title: str,
        task_goal: str,
        context: str = "",
        expected_output: str = "implementation advice, risks, file plan and validation steps",
        target_project: str = "GOD_MODE",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        session = self._find("work_sessions", "work_session_id", work_session_id)
        if not session:
            return {"ok": False, "mode": "create_work_packet", "error": "work_session_not_found", "work_session_id": work_session_id}
        provider_key = self._provider_key(provider)
        prompt = self._build_provider_prompt(session, provider_key, task_title, task_goal, context, expected_output, target_project)
        packet = {
            "work_packet_id": f"ia-work-packet-{uuid4().hex[:12]}",
            "work_session_id": work_session_id,
            "created_at": self._now(),
            "updated_at": self._now(),
            "tenant_id": tenant_id,
            "provider": provider_key,
            "task_title": task_title[:220],
            "task_goal": self._sanitize(task_goal)[:2000],
            "context": self._sanitize(context)[:4000],
            "expected_output": expected_output[:1000],
            "target_project": target_project[:120],
            "status": "drafted",
            "prompt": prompt,
            "manual_send_required": True,
            "can_auto_send": False,
            "can_store_secrets": False,
            "safe_next_step": "Review packet, then manually send/capture provider response when safe. Oner should not interact while driving.",
        }
        self._store("work_packets", packet)
        return {"ok": True, "mode": "create_ia_work_packet", "work_packet": packet}

    def create_packets_from_self_diagnosis(
        self,
        work_session_id: str,
        providers: List[str] | None = None,
        limit: int = 5,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        providers = providers or ["chatgpt", "claude", "gemini"]
        queue = god_mode_self_diagnosis_mission_control_service.list_queue(limit=limit).get("self_fix_queue", [])
        packets = []
        for index, item in enumerate(queue[:limit]):
            provider = providers[index % len(providers)]
            result = self.create_work_packet(
                work_session_id=work_session_id,
                provider=provider,
                task_title=f"Self-fix analysis: {item.get('title')}",
                task_goal=f"Analyze this God Mode gap and propose a safe native fix plan: {item.get('reason')} Next step: {item.get('recommended_next_step')}",
                context=f"self_fix_queue_item_id={item.get('self_fix_queue_item_id')} target_module={item.get('target_module')} severity={item.get('severity')} install_blocker={item.get('install_blocker')}",
                expected_output="return concise implementation plan, affected files, risks, tests, and whether Oner approval is needed",
                target_project="GOD_MODE",
                tenant_id=tenant_id,
            )
            if result.get("ok"):
                packets.append(result["work_packet"])
        return {"ok": True, "mode": "create_packets_from_self_diagnosis", "packet_count": len(packets), "work_packets": packets}

    def mark_packet_status(self, work_packet_id: str, status: str, note: str = "", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        if status not in WORK_PACKET_STATUSES:
            return {"ok": False, "mode": "mark_packet_status", "error": "invalid_status", "allowed_statuses": sorted(WORK_PACKET_STATUSES)}
        packet = self._find("work_packets", "work_packet_id", work_packet_id)
        if not packet:
            return {"ok": False, "mode": "mark_packet_status", "error": "work_packet_not_found", "work_packet_id": work_packet_id}
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for item in state.get("work_packets", []):
                if item.get("work_packet_id") == work_packet_id:
                    item["status"] = status
                    item["updated_at"] = self._now()
                    item["status_note"] = self._sanitize(note)[:1000]
            return state
        IA_WORK_SESSION_STORE.update(mutate)
        self._log("mark_packet_status", work_packet_id, status, note, tenant_id)
        return {"ok": True, "mode": "mark_packet_status", "work_packet": self._find("work_packets", "work_packet_id", work_packet_id)}

    def import_response(
        self,
        work_packet_id: str,
        response_text: str,
        provider: str = "manual_ai",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        packet = self._find("work_packets", "work_packet_id", work_packet_id)
        if not packet:
            return {"ok": False, "mode": "import_ia_response", "error": "work_packet_not_found", "work_packet_id": work_packet_id}
        cleaned = self._sanitize(response_text)
        transcript = f"Oner: Work packet {work_packet_id} for {packet.get('target_project')} - {packet.get('task_title')}\n\nAssistant: {cleaned}"
        imported = conversation_source_import_feed_service.import_text(
            transcript_text=transcript,
            provider=provider or packet.get("provider") or "manual_ai",
            project_hint=packet.get("target_project", "GOD_MODE"),
            title=f"IA response for {packet.get('task_title')}",
            source_ref=work_packet_id,
            tenant_id=tenant_id,
            create_review_card=False,
        )
        response_item = {
            "response_import_id": f"ia-response-import-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "work_packet_id": work_packet_id,
            "provider": provider or packet.get("provider"),
            "conversation_import_id": imported.get("import", {}).get("import_id"),
            "ledger_analysis_id": imported.get("import", {}).get("ledger_analysis_id"),
            "response_preview": cleaned[:1000],
            "converted_to_tasks": False,
            "stores_secrets": False,
        }
        self._store("response_imports", response_item)
        self.mark_packet_status(work_packet_id, "response_imported", note="Response imported into conversation source feed", tenant_id=tenant_id)
        return {"ok": True, "mode": "import_ia_response", "response_import": response_item, "conversation_import": imported}

    def convert_response_to_tasks(self, work_packet_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        packet = self._find("work_packets", "work_packet_id", work_packet_id)
        responses = [item for item in IA_WORK_SESSION_STORE.load().get("response_imports", []) if item.get("work_packet_id") == work_packet_id]
        if not packet or not responses:
            return {"ok": False, "mode": "convert_response_to_tasks", "error": "packet_or_response_missing", "work_packet_id": work_packet_id}
        tasks = [
            {
                "task_id": f"ia-derived-task-{uuid4().hex[:10]}",
                "title": f"Review IA response for {packet.get('task_title')}",
                "target_project": packet.get("target_project"),
                "source_packet_id": work_packet_id,
                "source_response_import_id": responses[-1].get("response_import_id"),
                "status": "needs_review",
                "requires_oner_for": ["merge", "release", "deploy", "paid API", "browser automation"] if self._looks_risky(responses[-1].get("response_preview", "")) else ["merge", "release"],
                "can_apply_directly": False,
            }
        ]
        self.mark_packet_status(work_packet_id, "converted_to_tasks", note="Converted into review tasks", tenant_id=tenant_id)
        return {"ok": True, "mode": "convert_response_to_tasks", "tasks": tasks, "can_apply_directly": False}

    def create_provider_launcher_contract(self, work_packet_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        packet = self._find("work_packets", "work_packet_id", work_packet_id)
        if not packet:
            return {"ok": False, "mode": "provider_launcher_contract", "error": "work_packet_not_found", "work_packet_id": work_packet_id}
        provider = packet.get("provider") or "chatgpt"
        try:
            contract = provider_browser_local_launcher_service.create_launcher_package(provider=provider, tenant_id=tenant_id)  # type: ignore[attr-defined]
        except Exception:
            contract = {"ok": True, "mode": "manual_provider_contract", "provider": provider, "manual_send_required": True, "prompt": packet.get("prompt")}
        return {"ok": True, "mode": "provider_launcher_contract", "work_packet": packet, "contract": contract, "manual_send_required": True}

    def list_packets(self, status: str | None = None, provider: str | None = None, limit: int = 100) -> Dict[str, Any]:
        limit = max(1, min(int(limit), 500))
        packets = list(IA_WORK_SESSION_STORE.load().get("work_packets", []))
        if status:
            packets = [item for item in packets if item.get("status") == status]
        if provider:
            packets = [item for item in packets if item.get("provider") == self._provider_key(provider)]
        packets.sort(key=lambda item: item.get("updated_at", item.get("created_at", "")), reverse=True)
        return {"ok": True, "mode": "ia_work_packet_list", "count": len(packets[:limit]), "work_packets": packets[:limit]}

    def dashboard(self) -> Dict[str, Any]:
        state = IA_WORK_SESSION_STORE.load()
        return {
            "ok": True,
            "mode": "autonomous_ia_work_session_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "work_sessions": state.get("work_sessions", [])[-100:],
            "work_packets": state.get("work_packets", [])[-200:],
            "response_imports": state.get("response_imports", [])[-200:],
            "review_cards": state.get("review_cards", [])[-100:],
            "decision_log": state.get("decision_log", [])[-150:],
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _build_provider_prompt(self, session: Dict[str, Any], provider: str, task_title: str, task_goal: str, context: str, expected_output: str, target_project: str) -> str:
        return "\n".join([
            "You are assisting the God Mode operator system.",
            f"Provider target: {provider}",
            f"Project: {target_project}",
            f"Session: {session.get('title')}",
            f"Task: {task_title}",
            "Goal:",
            self._sanitize(task_goal),
            "Context:",
            self._sanitize(context),
            "Required output:",
            expected_output,
            "Rules:",
            "- Do not request or include tokens, passwords, cookies, private keys or raw secrets.",
            "- Do not propose blind merge/release/deploy/browser automation.",
            "- Prefer native implementation inside God Mode when sensible.",
            "- Give affected files, risks, validation checks and gates.",
            "- Separate safe next steps from actions requiring Oner approval.",
        ])

    def _sanitize(self, text: str) -> str:
        lines = []
        for line in (text or "").splitlines():
            lowered = line.lower()
            if any(key in lowered for key in ["api_key=", "token=", "password=", "cookie=", "secret="]):
                lines.append("[REDACTED_SECRET_LINE]")
            else:
                lines.append(line)
        return "\n".join(lines).strip()

    def _provider_key(self, provider: str) -> str:
        key = re.sub(r"[^a-z0-9_\-]+", "_", (provider or "manual_ai").lower()).strip("_")
        return key if key in SAFE_PROVIDERS else "manual_ai"

    def _looks_risky(self, text: str) -> bool:
        lower = (text or "").lower()
        return any(word in lower for word in ["deploy", "release", "payment", "api key", "browser automation", "cookie", "token", "credential"])

    def _find(self, bucket: str, key: str, value: str) -> Dict[str, Any] | None:
        return next((item for item in IA_WORK_SESSION_STORE.load().get(bucket, []) if item.get(key) == value), None)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1500:]
            return state
        IA_WORK_SESSION_STORE.update(mutate)

    def _log(self, action: str, item_id: str, decision: str, reason: str, tenant_id: str) -> None:
        self._store("decision_log", {"created_at": self._now(), "tenant_id": tenant_id, "action": action, "item_id": item_id, "decision": decision, "reason": self._sanitize(reason)[:1000]})

    def _create_session_card(self, session: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        result = mobile_approval_cockpit_v2_service.create_card(
            title=f"IA work session criada: {session.get('title')}",
            body="God Mode pode preparar pacotes para IAs enquanto Oner está ocupado; envio/captura/provider privado continuam manuais/gated.",
            card_type="autonomous_ia_work_session",
            project_id=session.get("project_id", "GOD_MODE"),
            tenant_id=tenant_id,
            priority="normal",
            requires_approval=False,
            actions=[{"action_id": "review-ia-work-session", "label": "Rever sessão IA", "decision": "review"}],
            source_ref={"type": "ia_work_session", "work_session_id": session.get("work_session_id")},
            metadata={"operator_mode": session.get("operator_mode"), "manual_provider_send_required": True},
        )
        card = result.get("card")
        if card:
            self._store("review_cards", card)
        return result


autonomous_ia_work_session_operator_service = AutonomousIaWorkSessionOperatorService()
