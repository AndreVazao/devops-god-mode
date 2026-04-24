from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.memory_core_service import memory_core_service
from app.services.mission_control_cockpit_service import mission_control_cockpit_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
LEARNING_ROUTER_FILE = DATA_DIR / "learning_router.json"
LEARNING_ROUTER_STORE = AtomicJsonStore(
    LEARNING_ROUTER_FILE,
    default_factory=lambda: {"patterns": [], "unknowns": [], "decisions": [], "stats": {"handled": 0, "unknown": 0}},
)

KNOWN_INTENTS = {
    "continue_project": ["continua", "continuar", "retomar", "segue", "avança", "proximo passo", "próximo passo"],
    "deep_audit": ["audita", "auditoria", "verifica", "lacunas", "ficheiros mortos", "quebras", "falhas"],
    "build_check": ["build", "checks", "artefact", "artifact", "apk", "exe", "github actions", "verde"],
    "memory_review": ["memoria", "memória", "obsidian", "ultima sessao", "última sessão", "decisoes", "decisões"],
    "fix_plan": ["corrige", "repara", "arruma", "plano de correcao", "plano de correção"],
    "delivery_summary": ["resumo", "entrega", "estado", "explica", "relatorio", "relatório"],
}

INTENT_TO_GUIDED_ACTION = {
    "continue_project": "continue-project",
    "deep_audit": "deep-audit",
    "build_check": "build-check",
    "memory_review": "memory-review",
    "fix_plan": "fix-plan",
    "delivery_summary": "delivery-summary",
}

PROJECT_ALIASES = {
    "god mode": "GOD_MODE",
    "godmode": "GOD_MODE",
    "proventil": "PROVENTIL",
    "verba forge": "VERBAFORGE",
    "verbaforge": "VERBAFORGE",
    "lords": "BOT_LORDS_MOBILE",
    "lords mobile": "BOT_LORDS_MOBILE",
    "bot lords": "BOT_LORDS_MOBILE",
    "botfarm": "BOT_LORDS_MOBILE",
    "ecu": "ECU_REPRO",
    "repro": "ECU_REPRO",
    "build control": "BUILD_CONTROL_CENTER",
    "build center": "BUILD_CONTROL_CENTER",
}


class LearningRouterService:
    """Adaptive command router for natural operator messages.

    It does not train opaque ML models. It stores explainable routing patterns,
    unknown utterances and operator corrections so God Mode can improve safely.
    """

    def get_status(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "learning_router_status",
            "status": "learning_router_ready",
            "store_file": str(LEARNING_ROUTER_FILE),
            "atomic_store_enabled": True,
            "pattern_count": len(store.get("patterns", [])),
            "unknown_count": len(store.get("unknowns", [])),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_store(self, store: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(store, dict):
            return {"patterns": [], "unknowns": [], "decisions": [], "stats": {"handled": 0, "unknown": 0}}
        store.setdefault("patterns", [])
        store.setdefault("unknowns", [])
        store.setdefault("decisions", [])
        store.setdefault("stats", {"handled": 0, "unknown": 0})
        store["stats"].setdefault("handled", 0)
        store["stats"].setdefault("unknown", 0)
        return store

    def _load_store(self) -> Dict[str, Any]:
        return self._normalize_store(LEARNING_ROUTER_STORE.load())

    def _detect_project(self, text: str, project_hint: str | None = None) -> str:
        if project_hint and project_hint.strip():
            return project_hint.upper().replace("-", "_").replace(" ", "_")
        lowered = text.lower()
        for alias, project in PROJECT_ALIASES.items():
            if alias in lowered:
                return project
        return "GOD_MODE"

    def _score_intent(self, text: str, store: Dict[str, Any]) -> Dict[str, Any]:
        lowered = text.lower()
        scores: Dict[str, int] = {intent: 0 for intent in KNOWN_INTENTS}
        matched: Dict[str, List[str]] = {intent: [] for intent in KNOWN_INTENTS}
        for intent, terms in KNOWN_INTENTS.items():
            for term in terms:
                if term in lowered:
                    scores[intent] += 2
                    matched[intent].append(term)
        for pattern in store.get("patterns", []):
            phrase = str(pattern.get("phrase", "")).lower().strip()
            intent = pattern.get("intent")
            if phrase and intent in scores and phrase in lowered:
                scores[intent] += int(pattern.get("weight", 4))
                matched[intent].append(f"learned:{phrase}")
        best_intent = max(scores, key=lambda key: scores[key])
        best_score = scores[best_intent]
        confidence = min(0.95, best_score / 8) if best_score else 0.0
        return {"intent": best_intent if best_score else "unknown", "score": best_score, "confidence": confidence, "matched_terms": matched.get(best_intent, [])}

    def route_message(self, message: str, project_hint: str | None = None, tenant_id: str = "owner-andre", auto_execute_confident: bool = True) -> Dict[str, Any]:
        text = message.strip()
        if not text:
            return {"ok": False, "error": "message_empty"}
        store = self._load_store()
        project = self._detect_project(text, project_hint)
        scored = self._score_intent(text, store)
        route_id = f"route-{uuid4().hex[:12]}"
        created_at = self._now()
        record = {
            "route_id": route_id,
            "created_at": created_at,
            "tenant_id": tenant_id,
            "message": text,
            "project": project,
            "intent": scored["intent"],
            "confidence": scored["confidence"],
            "matched_terms": scored["matched_terms"],
            "status": "planned",
        }
        result: Dict[str, Any] | None = None
        if scored["intent"] != "unknown" and scored["confidence"] >= 0.45:
            action_id = INTENT_TO_GUIDED_ACTION[scored["intent"]]
            record["guided_action_id"] = action_id
            if auto_execute_confident:
                result = mission_control_cockpit_service.submit_mobile_command(
                    command_text=f"{text}\n\nRota aprendida: {scored['intent']} -> {action_id}. Usa a memória AndreOS e mantém aprovações obrigatórias.",
                    project_hint=project,
                    tenant_id=tenant_id,
                )
                record["status"] = "routed_to_mission_control"
        else:
            record["status"] = "unknown_needs_ai_or_operator_review"
            record["recommended_action"] = "forward_to_chat_web_for_interpretation"

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload["decisions"].append(record)
            payload["decisions"] = payload["decisions"][-1000:]
            if record["status"] == "unknown_needs_ai_or_operator_review":
                payload["unknowns"].append(record)
                payload["unknowns"] = payload["unknowns"][-500:]
                payload["stats"]["unknown"] += 1
            else:
                payload["stats"]["handled"] += 1
            return payload

        LEARNING_ROUTER_STORE.update(mutate)
        memory_core_service.write_history(
            project,
            action="Learning Router processed operator message",
            result=f"Intent: {record['intent']} | Confidence: {record['confidence']:.2f} | Status: {record['status']}",
        )
        return {"ok": True, "mode": "learning_router_route_message", "route": record, "mission_control": result}

    def learn_pattern(self, phrase: str, intent: str, action_id: str | None = None, project: str = "GOD_MODE", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        normalized_intent = intent.strip().lower()
        if normalized_intent not in INTENT_TO_GUIDED_ACTION:
            return {"ok": False, "error": "invalid_intent", "allowed": sorted(INTENT_TO_GUIDED_ACTION.keys())}
        normalized_phrase = phrase.strip().lower()
        if not normalized_phrase:
            return {"ok": False, "error": "phrase_empty"}
        pattern = {
            "pattern_id": f"pattern-{uuid4().hex[:12]}",
            "phrase": normalized_phrase,
            "intent": normalized_intent,
            "action_id": action_id or INTENT_TO_GUIDED_ACTION[normalized_intent],
            "project": project,
            "tenant_id": tenant_id,
            "weight": 5,
            "created_at": self._now(),
        }

        def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
            payload = self._normalize_store(payload)
            payload["patterns"] = [item for item in payload.get("patterns", []) if item.get("phrase") != normalized_phrase]
            payload["patterns"].append(pattern)
            payload["patterns"] = payload["patterns"][-500:]
            return payload

        LEARNING_ROUTER_STORE.update(mutate)
        memory_core_service.write_decision(project, f"Learning Router aprendeu frase '{normalized_phrase}' como {normalized_intent}.", "Correção/treino do operador.")
        return {"ok": True, "mode": "learning_router_learn_pattern", "pattern": pattern}

    def list_unknowns(self, limit: int = 50) -> Dict[str, Any]:
        store = self._load_store()
        unknowns = store.get("unknowns", [])[-max(min(limit, 200), 1):]
        return {"ok": True, "mode": "learning_router_unknown_list", "unknown_count": len(unknowns), "unknowns": unknowns}

    def build_dashboard(self) -> Dict[str, Any]:
        store = self._load_store()
        return {
            "ok": True,
            "mode": "learning_router_dashboard",
            "stats": store.get("stats", {}),
            "pattern_count": len(store.get("patterns", [])),
            "unknown_count": len(store.get("unknowns", [])),
            "recent_decisions": store.get("decisions", [])[-30:],
            "recent_unknowns": store.get("unknowns", [])[-20:],
            "patterns": store.get("patterns", [])[-50:],
            "intents": sorted(INTENT_TO_GUIDED_ACTION.keys()),
        }

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "learning_router_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


learning_router_service = LearningRouterService()
