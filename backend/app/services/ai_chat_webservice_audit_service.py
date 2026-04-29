from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.services.operator_chat_real_work_bridge_service import operator_chat_real_work_bridge_service
from app.services.operator_conversation_thread_service import operator_conversation_thread_service


class AiChatWebserviceAuditService:
    """Audit whether God Mode can communicate with external AI chat services.

    This audit is intentionally strict. Internal operator chat is not the same as
    browser/web-service control of external AI chats. The report separates what
    already exists from what still needs implementation.
    """

    REQUIRED_CAPABILITIES = [
        "internal_operator_chat_bridge",
        "conversation_thread_store",
        "external_ai_registry",
        "external_chat_open_session",
        "external_chat_read_visible_messages",
        "external_chat_scroll_history",
        "external_chat_send_prompt",
        "external_chat_wait_for_response",
        "external_chat_extract_response",
        "external_chat_safety_gate",
    ]

    SEARCH_MARKERS = {
        "browser_automation": ["playwright", "selenium", "browser", "page.goto", "locator", "webdriver"],
        "scroll_support": ["scroll", "scroll_to", "mouse.wheel", "window.scroll", "scrollIntoView"],
        "message_extraction": ["inner_text", "text_content", "query_selector", "conversation", "messages"],
        "prompt_injection": ["send_prompt", "fill(", "press(", "textarea", "contenteditable", "input"],
        "external_ai": ["chatgpt", "claude", "gemini", "mistral", "perplexity", "external_ai"],
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def build_audit(self) -> Dict[str, Any]:
        repo_scan = self._repo_scan()
        bridge = operator_chat_real_work_bridge_service.get_status()
        threads = operator_conversation_thread_service.get_status()
        checks = [
            self._check(
                "internal_operator_chat_bridge",
                "Chat interno operador → trabalho real existe",
                bridge.get("status") == "chat_to_real_work_ready",
                bridge,
            ),
            self._check(
                "conversation_thread_store",
                "Threads internas de conversa existem",
                threads.get("status") == "operator_conversation_thread_ready",
                threads,
            ),
            self._check(
                "external_ai_registry",
                "Registo de IAs externas existe",
                repo_scan["marker_hits"].get("external_ai", {}).get("hit_count", 0) > 0,
                repo_scan["marker_hits"].get("external_ai", {}),
            ),
            self._check(
                "external_chat_open_session",
                "Abrir sessão/browser de chat externo existe",
                repo_scan["marker_hits"].get("browser_automation", {}).get("hit_count", 0) > 0,
                repo_scan["marker_hits"].get("browser_automation", {}),
            ),
            self._check(
                "external_chat_read_visible_messages",
                "Ler mensagens visíveis de chat externo existe",
                repo_scan["marker_hits"].get("message_extraction", {}).get("hit_count", 0) > 0,
                repo_scan["marker_hits"].get("message_extraction", {}),
            ),
            self._check(
                "external_chat_scroll_history",
                "Scroll para histórico de conversa externa existe",
                repo_scan["marker_hits"].get("scroll_support", {}).get("hit_count", 0) > 0,
                repo_scan["marker_hits"].get("scroll_support", {}),
            ),
            self._check(
                "external_chat_send_prompt",
                "Enviar prompt/pergunta para IA externa existe",
                repo_scan["marker_hits"].get("prompt_injection", {}).get("hit_count", 0) > 0,
                repo_scan["marker_hits"].get("prompt_injection", {}),
            ),
            self._check(
                "external_chat_wait_for_response",
                "Esperar resposta de IA externa existe",
                False,
                "Nenhum worker externo dedicado encontrado nesta auditoria estática.",
            ),
            self._check(
                "external_chat_extract_response",
                "Extrair resposta final da IA externa existe",
                False,
                "Nenhum extractor externo dedicado encontrado nesta auditoria estática.",
            ),
            self._check(
                "external_chat_safety_gate",
                "Gate de segurança para prompts externos existe",
                False,
                "Ainda precisa política própria para não enviar segredos/código sensível sem confirmação.",
            ),
        ]
        failed = [item for item in checks if not item["ok"]]
        score = round((sum(1 for item in checks if item["ok"]) / len(checks)) * 100) if checks else 0
        status = "ready" if not failed else ("partial" if score >= 40 else "not_ready")
        return {
            "ok": not failed,
            "mode": "ai_chat_webservice_audit",
            "created_at": self._now(),
            "status": status,
            "score": score,
            "checks": checks,
            "failed_checks": failed,
            "repo_scan": repo_scan,
            "honest_conclusion": self._conclusion(status=status, score=score, failed=failed),
            "recommended_phases": self._recommended_phases(failed),
            "operator_next": self._operator_next(failed),
        }

    def _repo_scan(self) -> Dict[str, Any]:
        roots = [Path("backend"), Path("frontend"), Path("desktop"), Path("mobile"), Path("docs")]
        files: List[Path] = []
        for root in roots:
            if root.exists():
                files.extend(path for path in root.rglob("*") if path.is_file() and path.suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".html"})
        marker_hits: Dict[str, Dict[str, Any]] = {}
        for group, markers in self.SEARCH_MARKERS.items():
            hits = []
            for path in files[:2500]:
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore").lower()
                except Exception:
                    continue
                found = [marker for marker in markers if marker.lower() in text]
                if found:
                    hits.append({"path": str(path), "markers": found[:8]})
            marker_hits[group] = {"hit_count": len(hits), "hits": hits[:20]}
        return {
            "scanned_file_count": len(files),
            "marker_hits": marker_hits,
            "note": "Static scan only. Passing markers does not prove external AI chat automation works end-to-end.",
        }

    def _check(self, check_id: str, label: str, ok: bool, detail: Any) -> Dict[str, Any]:
        return {"id": check_id, "label": label, "ok": bool(ok), "detail": detail}

    def _conclusion(self, status: str, score: int, failed: List[Dict[str, Any]]) -> str:
        if status == "ready":
            return f"God Mode parece pronto para controlar chats externos de IA. Score {score}%."
        if status == "partial":
            return f"God Mode tem base interna de chat, mas ainda não está provado que consiga ler, scrollar, escrever e recolher respostas em chats externos de IAs. Score {score}%."
        return f"God Mode ainda não tem camada suficiente para falar com chats externos de IAs. Score {score}%."

    def _recommended_phases(self, failed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        needed = {item["id"] for item in failed}
        phases: List[Dict[str, Any]] = []
        if needed & {"external_ai_registry", "external_chat_open_session"}:
            phases.append({"phase": "external_ai_registry_and_session", "label": "Criar registo de IAs externas e sessões controladas"})
        if needed & {"external_chat_read_visible_messages", "external_chat_scroll_history"}:
            phases.append({"phase": "external_chat_reader_scroll", "label": "Criar leitor de mensagens e scroll de histórico"})
        if needed & {"external_chat_send_prompt", "external_chat_wait_for_response", "external_chat_extract_response"}:
            phases.append({"phase": "external_chat_prompt_response", "label": "Criar envio de prompt e extração de resposta"})
        if needed & {"external_chat_safety_gate"}:
            phases.append({"phase": "external_chat_safety_gate", "label": "Criar gate de segurança para prompts externos"})
        return phases

    def _operator_next(self, failed: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not failed:
            return {"label": "Testar chat externo", "endpoint": "/api/ai-chat-webservice-audit/audit", "route": "/app/home"}
        return {"label": "Implementar camada de chat externo", "endpoint": "/api/ai-chat-webservice-audit/audit", "route": "/app/home"}

    def get_status(self) -> Dict[str, Any]:
        audit = self.build_audit()
        return {
            "ok": audit["ok"],
            "mode": "ai_chat_webservice_audit_status",
            "status": audit["status"],
            "score": audit["score"],
            "failed_count": len(audit["failed_checks"]),
            "operator_next": audit["operator_next"],
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "ai_chat_webservice_audit_package", "package": {"status": self.get_status(), "audit": self.build_audit()}}


ai_chat_webservice_audit_service = AiChatWebserviceAuditService()
