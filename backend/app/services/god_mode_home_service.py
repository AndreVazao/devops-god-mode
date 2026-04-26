from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.guided_mobile_command_center_service import guided_mobile_command_center_service
from app.services.memory_core_service import DEFAULT_BLOCKED_KEYWORDS, memory_core_service
from app.services.mission_control_cockpit_service import mission_control_cockpit_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.services.money_command_center_service import money_command_center_service
from app.services.operator_chat_runtime_snapshot_service import operator_chat_runtime_snapshot_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service
from app.services.project_portfolio_service import project_portfolio_service
from app.services.self_update_service import self_update_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
GOD_MODE_HOME_FILE = DATA_DIR / "god_mode_home.json"
GOD_MODE_HOME_STORE = AtomicJsonStore(
    GOD_MODE_HOME_FILE,
    default_factory=lambda: {"actions": [], "sessions": [], "chat_events": []},
)

SECRET_WORDS = [item.lower() for item in DEFAULT_BLOCKED_KEYWORDS]


class GodModeHomeService:
    """Phone-first home cockpit with one-tap actions and ChatGPT-style continuous conversation."""

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "god_mode_home_status",
            "status": "god_mode_home_ready",
            "store_file": str(GOD_MODE_HOME_FILE),
            "atomic_store_enabled": True,
            "chat_first": True,
            "apk_ready_surface": True,
            "action_count": len(store.get("actions", [])),
            "session_count": len(store.get("sessions", [])),
            "chat_event_count": len(store.get("chat_events", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"actions": [], "sessions": [], "chat_events": []}
        store.setdefault("actions", [])
        store.setdefault("sessions", [])
        store.setdefault("chat_events", [])
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(GOD_MODE_HOME_STORE.load())

    def _safe_call(self, label: str, fn: Any) -> Dict[str, Any]:
        try:
            return {"ok": True, "label": label, "result": fn()}
        except Exception as exc:  # pragma: no cover - defensive home cockpit shield
            return {"ok": False, "label": label, "error": str(exc)}

    def _contains_secret_keyword(self, text: str) -> bool:
        lowered = text.lower()
        return any(re.search(rf"(?<![a-z0-9_]){re.escape(word)}(?![a-z0-9_])", lowered) for word in SECRET_WORDS)

    def _safe_chat_text(self, text: str) -> Dict[str, Any]:
        clean = (text or "").strip()
        if not clean:
            return {"ok": False, "error": "empty_message", "safe_text": ""}
        if self._contains_secret_keyword(clean):
            return {
                "ok": False,
                "error": "secret_like_text_blocked",
                "safe_text": "[Mensagem bloqueada: parece conter token/password/secret. Não colar segredos no chat.]",
            }
        return {"ok": True, "safe_text": clean[:4000]}

    def _remember(self, title: str, body: str) -> Dict[str, Any]:
        memory_core_service.initialize()
        return {
            "history": memory_core_service.write_history("GOD_MODE", title, body),
            "last_session": memory_core_service.update_last_session("GOD_MODE", f"God Mode Home: {title}", body),
        }

    def _open_buttons(self) -> List[Dict[str, Any]]:
        return [
            {"button_id": "open-chat", "label": "Chat corrido", "kind": "open", "url": "/app/operator-chat-sync", "priority": "critical"},
            {"button_id": "open-money", "label": "Ganhar dinheiro", "kind": "open", "url": "/app/money-command-center", "priority": "high"},
            {"button_id": "open-approvals", "label": "Aprovações", "kind": "open", "url": "/app/mobile-approval-cockpit-v2", "priority": "high"},
            {"button_id": "open-mission", "label": "Mission Control", "kind": "open", "url": "/app/mission-control", "priority": "medium"},
            {"button_id": "open-guided", "label": "Comandos guiados", "kind": "open", "url": "/app/guided-command-center", "priority": "medium"},
            {"button_id": "open-builds", "label": "Builds", "kind": "open", "url": "/app/build-catalog", "priority": "medium"},
            {"button_id": "open-memory", "label": "Memória", "kind": "open", "url": "/app/memory-core", "priority": "medium"},
            {"button_id": "open-self-update", "label": "Atualizar God Mode", "kind": "open", "url": "/app/self-update", "priority": "medium"},
        ]

    def _one_tap_buttons(self) -> List[Dict[str, Any]]:
        return [
            {"button_id": "one-tap-money", "label": "Criar próximo passo para dinheiro", "kind": "execute", "endpoint": "/api/god-mode-home/one-tap", "payload": {"action_id": "one-tap-money"}, "risk": "creates_approval_card"},
            {"button_id": "one-tap-continue-god-mode", "label": "Continuar God Mode", "kind": "execute", "endpoint": "/api/god-mode-home/one-tap", "payload": {"action_id": "one-tap-continue-god-mode"}, "risk": "creates_approval_card"},
            {"button_id": "one-tap-review-memory", "label": "Rever memória", "kind": "execute", "endpoint": "/api/god-mode-home/one-tap", "payload": {"action_id": "one-tap-review-memory"}, "risk": "safe_planning"},
        ]

    def _summary_from_snapshots(self, mission: Dict[str, Any], money: Dict[str, Any], approvals: Dict[str, Any], portfolio: Dict[str, Any], update: Dict[str, Any], chat: Dict[str, Any]) -> Dict[str, Any]:
        mission_result = mission.get("result", {}) if mission.get("ok") else {}
        money_result = money.get("result", {}) if money.get("ok") else {}
        approvals_result = approvals.get("result", {}) if approvals.get("ok") else {}
        portfolio_result = portfolio.get("result", {}) if portfolio.get("ok") else {}
        update_result = update.get("result", {}) if update.get("ok") else {}
        chat_result = chat.get("result", {}) if chat.get("ok") else {}
        return {
            "readiness": mission_result.get("readiness", "unknown"),
            "pending_approvals": approvals_result.get("pending_approval_count", 0),
            "top_money_project": (money_result.get("top_project") or {}).get("project_id"),
            "top_money_answer": money_result.get("operator_answer", ""),
            "project_count": portfolio_result.get("summary", {}).get("project_count", 0),
            "git_available": update_result.get("status", {}).get("git_available"),
            "chat_threads": chat_result.get("thread_count", 0),
            "chat_waiting_threads": chat_result.get("waiting_thread_count", 0),
            "chat_pending_gates": chat_result.get("pending_gate_count", 0),
        }

    def _choose_next_action(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        if summary.get("chat_pending_gates", 0) > 0 or summary.get("chat_waiting_threads", 0) > 0:
            return {"action_id": "open-chat", "label": "Tens conversa pendente no APK/chat. Continua no chat corrido.", "button_label": "Abrir chat", "url": "/app/operator-chat-sync", "reason": "O modo principal no APK é conversa contínua com estado inline.", "urgency": "critical"}
        if summary.get("pending_approvals", 0) > 0:
            return {"action_id": "open-approvals", "label": "Tens aprovações pendentes. Decide primeiro.", "button_label": "Abrir aprovações", "url": "/app/mobile-approval-cockpit-v2", "reason": "A execução segura depende de decisões explícitas.", "urgency": "high"}
        if summary.get("top_money_project"):
            return {"action_id": "one-tap-money", "label": f"Ataca dinheiro agora: {summary.get('top_money_project')}.", "button_label": "Criar próximo passo para dinheiro", "endpoint": "/api/god-mode-home/one-tap", "reason": summary.get("top_money_answer") or "Existe projeto com caminho comercial calculado.", "urgency": "high"}
        if summary.get("readiness") == "red":
            return {"action_id": "open-mission", "label": "Há bloqueio técnico. Abre Mission Control.", "button_label": "Abrir Mission Control", "url": "/app/mission-control", "reason": "Readiness geral está vermelho.", "urgency": "high"}
        return {"action_id": "one-tap-continue-god-mode", "label": "Continua o God Mode com comando guiado.", "button_label": "Continuar God Mode", "endpoint": "/api/god-mode-home/one-tap", "reason": "Sem bloqueio óbvio; avançar por fase pequena.", "urgency": "medium"}

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        mission = self._safe_call("mission_control", lambda: mission_control_cockpit_service.build_dashboard(tenant_id=tenant_id))
        money = self._safe_call("money_command_center", lambda: money_command_center_service.build_dashboard(tenant_id=tenant_id))
        approvals = self._safe_call("mobile_approvals", lambda: mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id))
        portfolio = self._safe_call("project_portfolio", lambda: project_portfolio_service.build_dashboard())
        update = self._safe_call("self_update", lambda: self_update_service.build_dashboard())
        chat = self._safe_call("operator_chat", lambda: operator_chat_runtime_snapshot_service.build_snapshot(tenant_id=tenant_id))
        summary = self._summary_from_snapshots(mission, money, approvals, portfolio, update, chat)
        next_action = self._choose_next_action(summary)
        session = {"session_id": f"home-session-{uuid4().hex[:12]}", "created_at": self._now(), "tenant_id": tenant_id, "summary": summary, "next_action": next_action}

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload["sessions"].append(session)
            payload["sessions"] = payload["sessions"][-100:]
            return payload

        GOD_MODE_HOME_STORE.update(mutate)
        store = self._load_store()
        return {
            "ok": True,
            "mode": "god_mode_home_dashboard",
            "tenant_id": tenant_id,
            "created_at": self._now(),
            "status": self.get_status(),
            "summary": summary,
            "next_action": next_action,
            "open_buttons": self._open_buttons(),
            "one_tap_buttons": self._one_tap_buttons(),
            "chat_contract": {
                "primary_apk_mode": "continuous_chat_like_chatgpt",
                "preferred_url": "/app/operator-chat-sync",
                "fallback_url": "/app/god-mode-home",
                "rules": [
                    "Conversas corridas são a superfície principal no APK.",
                    "Botões devem aparecer como ações sugeridas dentro do chat.",
                    "Aprovações, inputs seguros e replay devem aparecer inline na conversa.",
                    "Não guardar segredos em memória AndreOS.",
                ],
            },
            "recent_actions": store.get("actions", [])[-20:],
            "operator_message": next_action["label"],
        }

    def run_one_tap(self, action_id: str, project_id: str = "GOD_MODE", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        normalized_project = project_id.upper().replace("-", "_").replace(" ", "_")
        if action_id == "one-tap-money":
            result = money_command_center_service.create_approval_card(max_projects=2, tenant_id=tenant_id)
            action_label = "Created money approval card"
        elif action_id == "one-tap-continue-god-mode":
            result = guided_mobile_command_center_service.execute_guided_action(
                project="GOD_MODE",
                action_id="continue-project",
                extra_instruction="Foca em tornar o God Mode brutalmente fácil de usar no telemóvel e no APK com conversas corridas tipo ChatGPT. Próxima fase pequena, sem alterações destrutivas.",
                tenant_id=tenant_id,
            )
            action_label = "Submitted guided God Mode continuation"
        elif action_id == "one-tap-review-memory":
            result = guided_mobile_command_center_service.execute_guided_action(project=normalized_project, action_id="memory-review", extra_instruction="Mostra o que falta para continuar em mobile-first e chat-first sem repetir contexto.", tenant_id=tenant_id)
            action_label = "Submitted guided memory review"
        else:
            return {"ok": False, "error": "unknown_one_tap_action", "allowed": ["one-tap-money", "one-tap-continue-god-mode", "one-tap-review-memory"]}
        event = {"event_id": f"home-action-{uuid4().hex[:12]}", "created_at": self._now(), "tenant_id": tenant_id, "action_id": action_id, "project_id": normalized_project, "label": action_label, "ok": bool(result.get("ok"))}

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload["actions"].append(event)
            payload["actions"] = payload["actions"][-200:]
            return payload

        GOD_MODE_HOME_STORE.update(mutate)
        memory = self._remember("God Mode Home one-tap action", f"{action_label}: {action_id} para {normalized_project}")
        return {"ok": True, "mode": "god_mode_home_one_tap", "event": event, "result": result, "memory": memory, "dashboard": self.build_dashboard(tenant_id=tenant_id)}

    def chat(self, message: str, thread_id: str | None = None, project_id: str = "GOD_MODE", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        safe = self._safe_chat_text(message)
        if thread_id:
            thread_result = operator_conversation_thread_service.get_thread(thread_id)
            if not thread_result.get("ok"):
                thread_result = operator_conversation_thread_service.open_thread(tenant_id=tenant_id, conversation_title="God Mode Home", channel_mode="apk_continuous_chat")
                thread_id = thread_result["thread"]["thread_id"]
        else:
            thread_result = operator_conversation_thread_service.open_thread(tenant_id=tenant_id, conversation_title="God Mode Home", channel_mode="apk_continuous_chat")
            thread_id = thread_result["thread"]["thread_id"]
        user_text = safe.get("safe_text", "")
        operator_conversation_thread_service.append_message(thread_id=thread_id, role="operator", content=user_text, operational_state="blocked_secret" if not safe.get("ok") else "active")
        if not safe.get("ok"):
            reply = "Bloqueei essa mensagem porque parece conter segredo. Não coloques tokens, passwords, cookies, bearer ou API keys no chat."
            suggested = ["Abrir aprovações", "Continuar sem segredos"]
        else:
            intent = self._chat_intent(user_text)
            action = self._intent_to_action(intent, project_id=project_id, tenant_id=tenant_id)
            reply = action["reply"]
            suggested = action["suggested_next_steps"]
        operator_conversation_thread_service.append_message(thread_id=thread_id, role="assistant", content=reply, operational_state="ready", suggested_next_steps=suggested)
        event = {"event_id": f"home-chat-{uuid4().hex[:12]}", "created_at": self._now(), "tenant_id": tenant_id, "thread_id": thread_id, "project_id": project_id, "blocked": not safe.get("ok")}

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload["chat_events"].append(event)
            payload["chat_events"] = payload["chat_events"][-300:]
            return payload

        GOD_MODE_HOME_STORE.update(mutate)
        return {"ok": True, "mode": "god_mode_home_chat", "thread_id": thread_id, "reply": reply, "suggested_next_steps": suggested, "event": event, "thread": operator_conversation_thread_service.get_thread(thread_id)}

    def _chat_intent(self, text: str) -> str:
        lowered = text.lower()
        if any(word in lowered for word in ["dinheiro", "ganhar", "vender", "receita", "monetizar"]):
            return "money"
        if any(word in lowered for word in ["continuar", "avança", "proxima", "próxima", "fase"]):
            return "continue"
        if any(word in lowered for word in ["memória", "memoria", "lembrar", "obsidian"]):
            return "memory"
        if any(word in lowered for word in ["aprovar", "aprovações", "aprovacoes", "decidir"]):
            return "approvals"
        return "home"

    def _intent_to_action(self, intent: str, project_id: str, tenant_id: str) -> Dict[str, Any]:
        if intent == "money":
            result = money_command_center_service.top_project()
            top = result.get("top_project", {}) if result.get("ok") else {}
            return {"reply": f"O caminho mais curto para dinheiro agora é {top.get('name', 'ver Money Command Center')}. Posso criar o cartão de aprovação do sprint.", "suggested_next_steps": ["Criar próximo passo para dinheiro", "Abrir Money Command Center"]}
        if intent == "continue":
            return {"reply": "Vou continuar por fase pequena e segura. O botão certo é Continuar God Mode.", "suggested_next_steps": ["Continuar God Mode", "Abrir Mission Control"]}
        if intent == "memory":
            return {"reply": f"Posso rever a memória AndreOS de {project_id} e transformar lacunas em próximos passos.", "suggested_next_steps": ["Rever memória", "Abrir Memória"]}
        if intent == "approvals":
            dashboard = mobile_approval_cockpit_v2_service.build_dashboard(tenant_id=tenant_id)
            return {"reply": f"Tens {dashboard.get('pending_approval_count', 0)} aprovações pendentes.", "suggested_next_steps": ["Abrir aprovações", "Abrir chat corrido"]}
        dashboard = self.build_dashboard(tenant_id=tenant_id)
        return {"reply": dashboard.get("operator_message", "Estou pronto. Usa dinheiro, continuar, memória ou aprovações."), "suggested_next_steps": [dashboard.get("next_action", {}).get("button_label", "Abrir Home"), "Abrir chat corrido"]}

    def driving_mode(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        dashboard = self.build_dashboard(tenant_id=tenant_id)
        next_action = dashboard.get("next_action", {})
        return {"ok": True, "mode": "god_mode_home_driving_mode", "speakable": [dashboard.get("operator_message", "Sem próxima ação."), f"Botão recomendado: {next_action.get('button_label', 'abrir painel')}.", "No APK, continua pela conversa corrida; evita escrever segredos."], "safe_buttons": [dashboard.get("next_action"), *dashboard.get("open_buttons", [])[:3]]}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "god_mode_home_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


god_mode_home_service = GodModeHomeService()
