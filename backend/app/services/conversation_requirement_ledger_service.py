from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
LEDGER_FILE = DATA_DIR / "conversation_requirement_ledger.json"
LEDGER_STORE = AtomicJsonStore(
    LEDGER_FILE,
    default_factory=lambda: {"version": 1, "analyses": [], "request_items": [], "decision_items": [], "script_items": [], "reconciliation_reports": []},
)

REQUEST_HINTS = (
    "quero", "preciso", "tem que", "deve", "não esquecer", "nao esquecer", "objetivo", "gostava", "pedi", "pedido", "faz", "avança", "avanca", "cria", "montar", "implementar", "corrigir", "guardar", "diferenciar", "comparar", "não quero", "nao quero",
)
DECISION_HINTS = (
    "decidido", "decisão", "decisao", "ficou", "vamos", "arquitetura", "implementado", "merged", "phase", "fase", "validado", "endpoint", "smoke", "workflow", "pr #", "merge commit",
)
MIGRATION_HINTS = (
    "migrou", "migramos", "migrar", "passou de", "em vez de", "deixou de", "antes", "agora", "pc", "cloud", "supabase", "render", "vercel", "local",
)
REALNESS_HINTS = (
    "real", "não fictício", "nao ficticio", "funcionar", "validado", "github actions", "smoke", "build", "merge", "artifact", "endpoint", "pr",
)
CODE_FENCE_RE = re.compile(r"```(?P<lang>[A-Za-z0-9_+\-.]*)\n(?P<code>.*?)```", re.DOTALL)
MESSAGE_RE = re.compile(r"(?im)^\s*(?P<label>user|utilizador|andre|andré|oner|assistant|assistente|chatgpt|claude|gemini|praison|ruflo|provider|ia|ai)\s*:\s*(?P<body>.*?)(?=^\s*(?:user|utilizador|andre|andré|oner|assistant|assistente|chatgpt|claude|gemini|praison|ruflo|provider|ia|ai)\s*:|\Z)", re.DOTALL)


class ConversationRequirementLedgerService:
    """Request-led conversation ledger.

    Separates operator requests from AI responses/decisions/scripts so the God
    Mode can preserve what Andre asked for, track drift/migrations, and compare
    real implementation against the original intent.
    """

    SERVICE_ID = "conversation_requirement_ledger"
    VERSION = "phase_187_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = LEDGER_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "ledger_file": str(LEDGER_FILE),
            "analysis_count": len(state.get("analyses", [])),
            "request_count": len(state.get("request_items", [])),
            "decision_count": len(state.get("decision_items", [])),
            "script_count": len(state.get("script_items", [])),
            "reconciliation_report_count": len(state.get("reconciliation_reports", [])),
            "request_led": True,
            "ai_responses_are_proposals_until_decision_or_validation": True,
            "realness_gate_required": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "The operator request is the source of intent. AI answers are proposals unless accepted, implemented and validated.",
                "separates": ["operator_request", "ai_response", "decision", "architecture_change", "script_block", "implementation_evidence", "open_requirement"],
                "preserves_old_requests": True,
                "handles_direction_changes": True,
                "example_direction_change": "God Mode started cloud/Supabase/Render/Vercel and migrated to PC brain + mobile cockpit; old requirements remain tracked unless explicitly dropped.",
                "realness_rule": "A feature is not marked real unless tied to code, endpoint, PR, merge, CI smoke/build or local runtime proof.",
                "blocked": ["treat AI suggestion as final decision without evidence", "discard old operator request silently", "merge divergent design without recording migration reason"],
            },
        }

    def analyze_text(self, project_key: str, transcript_text: str, source_provider: str = "unknown", source_id: str | None = None, store: bool = True) -> Dict[str, Any]:
        messages = self._parse_messages(transcript_text, source_provider=source_provider)
        return self.analyze_messages(project_key=project_key, messages=messages, source_provider=source_provider, source_id=source_id, store=store)

    def analyze_messages(self, project_key: str, messages: List[Dict[str, Any]], source_provider: str = "unknown", source_id: str | None = None, store: bool = True) -> Dict[str, Any]:
        analysis_id = f"conv-ledger-{uuid4().hex[:12]}"
        normalized_messages = [self._normalize_message(item, source_provider, index + 1) for index, item in enumerate(messages)]
        requests = self._extract_requests(project_key, analysis_id, normalized_messages)
        decisions = self._extract_decisions(project_key, analysis_id, normalized_messages)
        scripts = self._extract_scripts(project_key, analysis_id, normalized_messages)
        migrations = self._extract_migrations(project_key, analysis_id, normalized_messages)
        report = self._reconcile(project_key, analysis_id, requests, decisions, migrations)
        analysis = {
            "analysis_id": analysis_id,
            "project_key": self._safe_project(project_key),
            "source_provider": source_provider,
            "source_id": source_id or analysis_id,
            "created_at": self._now(),
            "message_count": len(normalized_messages),
            "operator_message_count": sum(1 for item in normalized_messages if item["role"] == "operator"),
            "ai_message_count": sum(1 for item in normalized_messages if item["role"] == "ai"),
            "request_count": len(requests),
            "decision_count": len(decisions),
            "script_count": len(scripts),
            "migration_count": len(migrations),
            "realness_gap_count": report["realness_gap_count"],
            "messages": [self._redact_message(item) for item in normalized_messages],
            "requests": requests,
            "decisions": decisions,
            "scripts": scripts,
            "migrations": migrations,
            "reconciliation_report": report,
            "stores_secret_values": False,
        }
        if store:
            self._store_analysis(analysis)
        return {"ok": True, "mode": "conversation_requirement_analysis", "analysis": analysis}

    def compare_project(self, project_key: str) -> Dict[str, Any]:
        state = LEDGER_STORE.load()
        project = self._safe_project(project_key)
        requests = [item for item in state.get("request_items", []) if item.get("project_key") == project]
        decisions = [item for item in state.get("decision_items", []) if item.get("project_key") == project]
        reports = [item for item in state.get("reconciliation_reports", []) if item.get("project_key") == project]
        migrations = []
        for report in reports:
            migrations.extend(report.get("migrations", []))
        combined = self._reconcile(project, f"project-rollup-{uuid4().hex[:10]}", requests, decisions, migrations)
        combined["source_analysis_count"] = len(reports)
        return {"ok": True, "mode": "conversation_project_request_decision_compare", "report": combined}

    def list_open_requirements(self, project_key: str | None = None) -> Dict[str, Any]:
        state = LEDGER_STORE.load()
        reports = state.get("reconciliation_reports", [])
        open_items = []
        for report in reports:
            if project_key and report.get("project_key") != self._safe_project(project_key):
                continue
            open_items.extend(report.get("open_requirements", []))
        dedup = {item.get("request_id"): item for item in open_items}
        return {"ok": True, "mode": "conversation_open_requirements", "open_count": len(dedup), "open_requirements": list(dedup.values())}

    def realness_scorecard(self, project_key: str) -> Dict[str, Any]:
        compare = self.compare_project(project_key)["report"]
        total = max(1, compare.get("request_count", 0))
        covered = compare.get("covered_request_count", 0)
        partial = compare.get("partial_request_count", 0)
        open_count = compare.get("open_request_count", 0)
        realness_score = round(((covered + partial * 0.5) / total) * 100)
        return {
            "ok": True,
            "mode": "conversation_realness_scorecard",
            "project_key": self._safe_project(project_key),
            "realness_score": realness_score,
            "request_count": total if compare.get("request_count", 0) else 0,
            "covered_request_count": covered,
            "partial_request_count": partial,
            "open_request_count": open_count,
            "rule": "Realness increases only when operator requests are linked to accepted decisions and implementation evidence.",
            "next_actions": compare.get("next_actions", []),
        }

    def package(self, project_key: str = "GOD_MODE") -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "project_compare": self.compare_project(project_key),
            "open_requirements": self.list_open_requirements(project_key),
            "realness_scorecard": self.realness_scorecard(project_key),
            "routes": {
                "analyze_text": "/api/conversation-requirement-ledger/analyze-text",
                "analyze_messages": "/api/conversation-requirement-ledger/analyze-messages",
                "compare_project": "/api/conversation-requirement-ledger/compare-project",
                "open_requirements": "/api/conversation-requirement-ledger/open-requirements",
                "realness_scorecard": "/api/conversation-requirement-ledger/realness-scorecard",
            },
        }

    def _parse_messages(self, text: str, source_provider: str) -> List[Dict[str, Any]]:
        matches = list(MESSAGE_RE.finditer(text or ""))
        if not matches:
            return [{"role": "unknown", "speaker": source_provider, "content": text or ""}]
        messages = []
        for match in matches:
            label = match.group("label").strip()
            messages.append({"role": self._role_from_label(label), "speaker": label, "content": match.group("body").strip()})
        return messages

    def _role_from_label(self, label: str) -> str:
        lowered = label.lower()
        if lowered in {"user", "utilizador", "andre", "andré", "oner"}:
            return "operator"
        if lowered in {"assistant", "assistente", "chatgpt", "claude", "gemini", "praison", "ruflo", "provider", "ia", "ai"}:
            return "ai"
        return "unknown"

    def _normalize_message(self, message: Dict[str, Any], provider: str, index: int) -> Dict[str, Any]:
        role = message.get("role") or self._role_from_label(str(message.get("speaker") or ""))
        content = str(message.get("content") or message.get("body") or "")
        return {
            "message_id": f"msg-{index:04d}-{self._fingerprint(content)[:8]}",
            "index": index,
            "role": role if role in {"operator", "ai", "system", "unknown"} else "unknown",
            "speaker": str(message.get("speaker") or provider or "unknown")[:120],
            "provider": str(message.get("provider") or provider or "unknown")[:120],
            "content": content,
            "content_fingerprint": self._fingerprint(content),
            "has_code": bool(CODE_FENCE_RE.search(content)),
        }

    def _extract_requests(self, project_key: str, analysis_id: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        items = []
        for message in messages:
            if message["role"] != "operator":
                continue
            fragments = self._split_fragments(message["content"])
            for fragment in fragments:
                if self._has_any(fragment, REQUEST_HINTS):
                    items.append(self._request_item(project_key, analysis_id, message, fragment))
        return items

    def _extract_decisions(self, project_key: str, analysis_id: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        items = []
        for message in messages:
            if message["role"] not in {"ai", "operator"}:
                continue
            fragments = self._split_fragments(message["content"])
            for fragment in fragments:
                if self._has_any(fragment, DECISION_HINTS) or self._has_any(fragment, REALNESS_HINTS):
                    items.append(self._decision_item(project_key, analysis_id, message, fragment))
        return items

    def _extract_scripts(self, project_key: str, analysis_id: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scripts = []
        for message in messages:
            for idx, match in enumerate(CODE_FENCE_RE.finditer(message["content"]), start=1):
                code = match.group("code")
                scripts.append({
                    "script_id": f"script-{uuid4().hex[:12]}",
                    "analysis_id": analysis_id,
                    "project_key": self._safe_project(project_key),
                    "source_role": message["role"],
                    "source_provider": message.get("provider"),
                    "message_id": message["message_id"],
                    "language": match.group("lang") or "text",
                    "line_count": len(code.splitlines()),
                    "code_fingerprint": self._fingerprint(code),
                    "content_preview": code[:240],
                    "script_origin_status": "ai_generated" if message["role"] == "ai" else "operator_supplied",
                    "requires_reconciliation_before_apply": True,
                })
        return scripts

    def _extract_migrations(self, project_key: str, analysis_id: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        migrations = []
        for message in messages:
            for fragment in self._split_fragments(message["content"]):
                if self._has_any(fragment, MIGRATION_HINTS) and ("pc" in fragment.lower() or "cloud" in fragment.lower() or "supabase" in fragment.lower() or "render" in fragment.lower() or "vercel" in fragment.lower()):
                    migrations.append({
                        "migration_id": f"migration-{uuid4().hex[:12]}",
                        "analysis_id": analysis_id,
                        "project_key": self._safe_project(project_key),
                        "message_id": message["message_id"],
                        "source_role": message["role"],
                        "summary": fragment[:500],
                        "migration_type": self._migration_type(fragment),
                        "preserve_original_requests": True,
                    })
        return migrations

    def _request_item(self, project_key: str, analysis_id: str, message: Dict[str, Any], text: str) -> Dict[str, Any]:
        return {
            "request_id": f"req-{uuid4().hex[:12]}",
            "analysis_id": analysis_id,
            "project_key": self._safe_project(project_key),
            "message_id": message["message_id"],
            "source_role": "operator",
            "request_text": text[:1200],
            "request_fingerprint": self._fingerprint(text),
            "priority": self._priority(text),
            "themes": self._themes(text),
            "status": "needs_decision_or_implementation_evidence",
        }

    def _decision_item(self, project_key: str, analysis_id: str, message: Dict[str, Any], text: str) -> Dict[str, Any]:
        evidence = self._evidence_type(text)
        return {
            "decision_id": f"dec-{uuid4().hex[:12]}",
            "analysis_id": analysis_id,
            "project_key": self._safe_project(project_key),
            "message_id": message["message_id"],
            "source_role": message["role"],
            "decision_text": text[:1200],
            "decision_fingerprint": self._fingerprint(text),
            "themes": self._themes(text),
            "evidence_type": evidence,
            "accepted_status": "operator_request" if message["role"] == "operator" else "ai_proposal_until_confirmed",
            "realness_status": "real_evidence" if evidence in {"merge_or_pr", "ci_or_build", "endpoint_or_code"} else "proposal_or_context",
        }

    def _reconcile(self, project_key: str, analysis_id: str, requests: List[Dict[str, Any]], decisions: List[Dict[str, Any]], migrations: List[Dict[str, Any]]) -> Dict[str, Any]:
        links = []
        open_reqs = []
        partial = []
        covered = []
        realness_gaps = []
        for req in requests:
            ranked = sorted(((self._overlap(req.get("themes", []), dec.get("themes", [])), dec) for dec in decisions), key=lambda x: x[0], reverse=True)
            best_score, best_decision = ranked[0] if ranked else (0, None)
            if best_decision and best_score >= 2:
                item = {"request_id": req["request_id"], "decision_id": best_decision["decision_id"], "coverage": "covered", "score": best_score, "realness_status": best_decision.get("realness_status")}
                links.append(item)
                covered.append(req)
                if best_decision.get("realness_status") != "real_evidence":
                    realness_gaps.append({"request_id": req["request_id"], "reason": "linked_decision_has_no_real_implementation_evidence", "request_text": req["request_text"]})
            elif best_decision and best_score == 1:
                item = {"request_id": req["request_id"], "decision_id": best_decision["decision_id"], "coverage": "partial", "score": best_score, "realness_status": best_decision.get("realness_status")}
                links.append(item)
                partial.append(req)
                realness_gaps.append({"request_id": req["request_id"], "reason": "partial_link_only", "request_text": req["request_text"]})
            else:
                open_reqs.append(req)
                realness_gaps.append({"request_id": req["request_id"], "reason": "no_decision_or_implementation_link", "request_text": req["request_text"]})
        return {
            "report_id": f"req-report-{uuid4().hex[:12]}",
            "analysis_id": analysis_id,
            "project_key": self._safe_project(project_key),
            "created_at": self._now(),
            "request_count": len(requests),
            "decision_count": len(decisions),
            "covered_request_count": len(covered),
            "partial_request_count": len(partial),
            "open_request_count": len(open_reqs),
            "realness_gap_count": len(realness_gaps),
            "links": links,
            "open_requirements": open_reqs,
            "partial_requirements": partial,
            "realness_gaps": realness_gaps,
            "migrations": migrations,
            "next_actions": self._next_actions(open_reqs, partial, realness_gaps),
        }

    def _store_analysis(self, analysis: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("analyses", []).append(analysis)
            state.setdefault("request_items", []).extend(analysis.get("requests", []))
            state.setdefault("decision_items", []).extend(analysis.get("decisions", []))
            state.setdefault("script_items", []).extend(analysis.get("scripts", []))
            state.setdefault("reconciliation_reports", []).append(analysis.get("reconciliation_report", {}))
            for key in ["analyses", "request_items", "decision_items", "script_items", "reconciliation_reports"]:
                state[key] = state.get(key, [])[-1000:]
            return state
        LEDGER_STORE.update(mutate)

    def _split_fragments(self, content: str) -> List[str]:
        clean = CODE_FENCE_RE.sub(" ", content or "")
        parts = re.split(r"(?<=[.!?])\s+|\n+|;", clean)
        return [part.strip() for part in parts if len(part.strip()) >= 12]

    def _has_any(self, text: str, hints: tuple[str, ...]) -> bool:
        lowered = text.lower()
        return any(hint in lowered for hint in hints)

    def _themes(self, text: str) -> List[str]:
        lowered = text.lower()
        themes = []
        mapping = {
            "vault": ["vault", "volte", "segredo", "secret", "token", "password", "chave"],
            "pc_brain": ["pc", "computador", "backend", "cérebro", "cerebro"],
            "mobile_cockpit": ["telemóvel", "telemovel", "telefone", "mobile", "cockpit"],
            "conversation_intake": ["conversa", "conversas", "ia", "respostas", "pedidos", "scripts"],
            "request_decision_diff": ["diferenciar", "comparar", "decidido", "pedido", "resposta"],
            "project_tree": ["tree", "árvore", "arvore", "estrutura"],
            "memory": ["memória", "memoria", "obsidian", "andreos"],
            "cloud_to_pc_migration": ["supabase", "render", "vercel", "cloud", "pc"],
            "realness": ["real", "fictício", "ficticio", "funcionar", "validado"],
            "deploy": ["deploy", "provider", "vercel", "render", "supabase", "github actions"],
        }
        for theme, hints in mapping.items():
            if any(hint in lowered for hint in hints):
                themes.append(theme)
        return sorted(set(themes)) or ["general"]

    def _priority(self, text: str) -> str:
        lowered = text.lower()
        if "não esquecer" in lowered or "nao esquecer" in lowered or "crítica" in lowered or "critica" in lowered or "tem que" in lowered:
            return "critical"
        if "preciso" in lowered or "objetivo" in lowered or "quero" in lowered:
            return "high"
        return "normal"

    def _evidence_type(self, text: str) -> str:
        lowered = text.lower()
        if "merge commit" in lowered or "pr #" in lowered or "merged" in lowered:
            return "merge_or_pr"
        if "smoke" in lowered or "build" in lowered or "github actions" in lowered or "validado" in lowered:
            return "ci_or_build"
        if "endpoint" in lowered or "/api/" in lowered or "serviço" in lowered or "rota" in lowered:
            return "endpoint_or_code"
        if "decidido" in lowered or "ficou" in lowered:
            return "decision_only"
        return "proposal"

    def _migration_type(self, text: str) -> str:
        lowered = text.lower()
        if "cloud" in lowered and "pc" in lowered:
            return "cloud_to_pc"
        if any(item in lowered for item in ["supabase", "render", "vercel"]) and "pc" in lowered:
            return "provider_cloud_to_pc"
        return "architecture_direction_change"

    def _overlap(self, a: List[str], b: List[str]) -> int:
        return len(set(a).intersection(set(b)))

    def _next_actions(self, open_reqs: List[Dict[str, Any]], partial: List[Dict[str, Any]], gaps: List[Dict[str, Any]]) -> List[str]:
        actions = []
        if open_reqs:
            actions.append("Create explicit decision or implementation plan for open operator requests.")
        if partial:
            actions.append("Review partial matches and confirm whether the current implementation still satisfies the original request.")
        if gaps:
            actions.append("Attach real evidence: endpoint, code path, PR, CI smoke, build artifact or local runtime proof.")
        return actions or ["No immediate reconciliation gap detected for this analysis."]

    def _redact_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(message)
        safe["content_preview"] = safe.pop("content", "")[:500]
        return safe

    def _safe_project(self, project_key: str) -> str:
        return re.sub(r"[^A-Za-z0-9_\-]+", "_", (project_key or "UNKNOWN_PROJECT").strip().upper()).strip("_") or "UNKNOWN_PROJECT"

    def _fingerprint(self, value: str) -> str:
        return hashlib.sha256((value or "").encode("utf-8", errors="ignore")).hexdigest()


conversation_requirement_ledger_service = ConversationRequirementLedgerService()
