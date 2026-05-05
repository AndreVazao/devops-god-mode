from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.first_real_install_launcher_service import first_real_install_launcher_service
from app.services.provider_prompt_broadcast_runtime_service import provider_prompt_broadcast_runtime_service
from app.services.conversation_requirement_ledger_service import conversation_requirement_ledger_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
FAST_PATH_FILE = DATA_DIR / "real_work_fast_path.json"
FAST_PATH_STORE = AtomicJsonStore(
    FAST_PATH_FILE,
    default_factory=lambda: {"version": 1, "project_groups": [], "repo_links": [], "conversation_links": [], "work_runs": []},
)

DEFAULT_GROUPS = [
    {
        "group_id": "baribudos_platform",
        "label": "Baribudos Platform",
        "description": "Website + Studio como duas frentes do mesmo programa/ecossistema.",
        "aliases": ["baribudos", "barbudo", "baribudos website", "baribudos studio", "very beach", "beybus", "barbudo studio"],
        "expected_fronts": ["website", "studio", "admin", "backend", "content"],
        "decision": "Treat website and studio as related fronts under one product group unless Oner separates them explicitly.",
    },
    {
        "group_id": "god_mode",
        "label": "DevOps God Mode",
        "description": "PC brain + mobile cockpit + DevOps automation + provider orchestration.",
        "aliases": ["god mode", "devops god mode", "andreos", "pc brain", "mobile cockpit"],
        "expected_fronts": ["backend", "android", "windows", "memory", "labs"],
        "decision": "God Mode is the main orchestrator; labs are references, not core dependencies.",
    },
    {
        "group_id": "proventil",
        "label": "ProVentil",
        "description": "Sistema de orçamentos/obras para ventilação e videoporteiros em Portugal.",
        "aliases": ["proventil", "video porteiro", "videoporteiro", "ventilação", "fumos"],
        "expected_fronts": ["crm", "quotes", "cad", "stock", "technician"],
        "decision": "Portuguese business system; keep separate from God Mode core.",
    },
]


class RealWorkFastPathService:
    """Practical first-use layer for real PC work intake and project/repo grouping."""

    SERVICE_ID = "real_work_fast_path"
    VERSION = "phase_193_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = self._state_with_defaults()
        install = first_real_install_launcher_service.get_status()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(FAST_PATH_FILE),
            "project_group_count": len(state.get("project_groups", [])),
            "repo_link_count": len(state.get("repo_links", [])),
            "conversation_link_count": len(state.get("conversation_links", [])),
            "work_run_count": len(state.get("work_runs", [])),
            "pc_install_status": install.get("status"),
            "pc_ready_to_launch": install.get("ready_to_launch"),
            "real_work_ready": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Map real work before automation: repos, conversations and product fronts must be grouped so the God Mode knows what belongs to what.",
                "operator_goal": "Use the phone to command the PC brain while driving/working, with approvals only for sensitive actions.",
                "realness_rule": "A project link is real when it has repo/conversation/evidence refs and a known group/front.",
                "blocked": ["guess destructive actions", "merge unrelated repos silently", "treat AI response as final decision", "store secrets in project map"],
                "allowed": ["classify repo", "link conversation", "group fronts", "create work run", "produce first PC checklist"],
            },
        }

    def seed_defaults(self) -> Dict[str, Any]:
        state = self._state_with_defaults(force_persist=True)
        return {"ok": True, "mode": "real_work_seed_defaults", "project_groups": state["project_groups"]}

    def add_project_group(self, label: str, aliases: List[str] | None = None, expected_fronts: List[str] | None = None, description: str = "") -> Dict[str, Any]:
        group = {
            "group_id": self._slug(label) or f"group-{uuid4().hex[:8]}",
            "label": label.strip()[:160],
            "description": description[:500],
            "aliases": sorted(set([self._norm(item) for item in (aliases or []) if item.strip()] + [self._norm(label)])),
            "expected_fronts": expected_fronts or [],
            "decision": "Operator-created project group.",
            "created_at": self._now(),
        }
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state = self._ensure_defaults_in_state(state)
            groups = [item for item in state.get("project_groups", []) if item.get("group_id") != group["group_id"]]
            groups.append(group)
            state["project_groups"] = groups[-500:]
            return state
        FAST_PATH_STORE.update(mutate)
        return {"ok": True, "mode": "real_work_project_group", "group": group}

    def link_repo(self, repo_full_name: str, project_hint: str | None = None, front: str | None = None, evidence: str | None = None) -> Dict[str, Any]:
        state = self._state_with_defaults()
        group = self._match_group(project_hint or repo_full_name, state.get("project_groups", []))
        link = {
            "repo_link_id": f"repo-link-{uuid4().hex[:12]}",
            "repo_full_name": repo_full_name.strip(),
            "project_hint": project_hint or "",
            "project_group_id": group.get("group_id") if group else "unclassified",
            "project_group_label": group.get("label") if group else "Unclassified",
            "front": self._front(front or repo_full_name),
            "evidence": evidence or "operator_or_repo_name_match",
            "created_at": self._now(),
            "realness_status": "linked_to_group" if group else "needs_operator_review",
        }
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state = self._ensure_defaults_in_state(state)
            links = [item for item in state.get("repo_links", []) if item.get("repo_full_name") != link["repo_full_name"]]
            links.append(link)
            state["repo_links"] = links[-1000:]
            return state
        FAST_PATH_STORE.update(mutate)
        return {"ok": True, "mode": "real_work_repo_link", "repo_link": link}

    def link_conversation(self, title: str, provider: str, project_hint: str, source_ref: str | None = None, summary: str = "") -> Dict[str, Any]:
        state = self._state_with_defaults()
        group = self._match_group(project_hint + " " + title, state.get("project_groups", []))
        conv = {
            "conversation_link_id": f"conversation-link-{uuid4().hex[:12]}",
            "title": title[:220],
            "provider": provider[:80],
            "project_hint": project_hint[:220],
            "project_group_id": group.get("group_id") if group else "unclassified",
            "project_group_label": group.get("label") if group else "Unclassified",
            "source_ref": source_ref or "manual_or_future_provider_import",
            "summary": summary[:1000],
            "created_at": self._now(),
            "realness_status": "linked_to_group" if group else "needs_operator_review",
        }
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state = self._ensure_defaults_in_state(state)
            state.setdefault("conversation_links", []).append(conv)
            state["conversation_links"] = state["conversation_links"][-1500:]
            return state
        FAST_PATH_STORE.update(mutate)
        return {"ok": True, "mode": "real_work_conversation_link", "conversation_link": conv}

    def classify_text(self, text: str) -> Dict[str, Any]:
        state = self._state_with_defaults()
        group = self._match_group(text, state.get("project_groups", []))
        front = self._front(text)
        confidence = "high" if group and front != "unknown" else "medium" if group else "low"
        return {
            "ok": True,
            "mode": "real_work_classify_text",
            "input_preview": text[:300],
            "project_group_id": group.get("group_id") if group else "unclassified",
            "project_group_label": group.get("label") if group else "Unclassified",
            "front": front,
            "confidence": confidence,
            "needs_operator_review": confidence == "low",
        }

    def create_work_run(self, operator_request: str, project_hint: str = "GOD_MODE", selected_provider_ids: List[str] | None = None) -> Dict[str, Any]:
        classification = self.classify_text(project_hint + " " + operator_request)
        broadcast = provider_prompt_broadcast_runtime_service.create_broadcast_plan(
            operator_request=operator_request,
            project_key=classification["project_group_id"].upper() if classification["project_group_id"] != "unclassified" else "GOD_MODE",
            selected_provider_ids=selected_provider_ids,
            use_prompt_critic=True,
            prompt_mode="real_work",
        )
        ledger = conversation_requirement_ledger_service.analyze_messages(
            project_key=classification["project_group_id"].upper() if classification["project_group_id"] != "unclassified" else "GOD_MODE",
            source_provider="god_mode_operator_intake",
            source_id="real_work_fast_path",
            store=True,
            messages=[{"role": "operator", "speaker": "Oner", "content": operator_request}],
        )
        run = {
            "work_run_id": f"work-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "operator_request": operator_request[:1200],
            "project_hint": project_hint,
            "classification": classification,
            "broadcast_plan_id": broadcast.get("plan", {}).get("plan_id"),
            "ledger_analysis_id": ledger.get("analysis", {}).get("analysis_id"),
            "status": "ready_for_provider_broadcast_or_manual_review",
            "next_routes": ["/app/provider-broadcast-cockpit", "/app/home"],
            "answers_are_decisions": False,
        }
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state = self._ensure_defaults_in_state(state)
            state.setdefault("work_runs", []).append(run)
            state["work_runs"] = state["work_runs"][-1000:]
            return state
        FAST_PATH_STORE.update(mutate)
        return {"ok": True, "mode": "real_work_run", "work_run": run, "broadcast": broadcast, "ledger": ledger}

    def first_pc_fast_path(self) -> Dict[str, Any]:
        install = first_real_install_launcher_service.get_package()
        state = self._state_with_defaults()
        essentials = [
            {"label": "Home", "route": "/app/home", "purpose": "cockpit principal"},
            {"label": "Broadcast IA", "route": "/app/provider-broadcast-cockpit", "purpose": "pedir a várias IAs e importar respostas"},
            {"label": "Mobile Approval", "route": "/app/mobile-approval-cockpit-v2", "purpose": "aprovar/atenção/login"},
            {"label": "Artifacts", "endpoint": "/api/artifacts-center/dashboard", "purpose": "confirmar APK/EXE"},
            {"label": "Real Work Fast Path", "endpoint": "/api/real-work-fast-path/package", "purpose": "mapa de trabalho real"},
        ]
        return {
            "ok": True,
            "mode": "first_pc_fast_path",
            "install": install,
            "essential_routes": essentials,
            "project_groups": state.get("project_groups", []),
            "minimum_real_test": [
                "Abrir GodModeDesktop.exe no PC.",
                "Confirmar /app/home.",
                "Abrir Broadcast IA.",
                "Criar plano com ChatGPT/Claude/Gemini.",
                "Gerar links/login cards.",
                "Colar uma resposta manual e comparar.",
                "Criar/confirmar link de repo/conversa no Real Work Map.",
            ],
        }

    def dashboard(self) -> Dict[str, Any]:
        state = self._state_with_defaults()
        return {
            "ok": True,
            "mode": "real_work_fast_path_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "project_groups": state.get("project_groups", []),
            "repo_links": state.get("repo_links", [])[-100:],
            "conversation_links": state.get("conversation_links", [])[-100:],
            "work_runs": state.get("work_runs", [])[-50:],
            "first_pc_fast_path": self.first_pc_fast_path(),
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _state_with_defaults(self, force_persist: bool = False) -> Dict[str, Any]:
        state = FAST_PATH_STORE.load()
        state = self._ensure_defaults_in_state(state)
        if force_persist:
            FAST_PATH_STORE.update(lambda _state: state)
        return state

    def _ensure_defaults_in_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        existing = {item.get("group_id") for item in state.get("project_groups", [])}
        groups = list(state.get("project_groups", []))
        for group in DEFAULT_GROUPS:
            if group["group_id"] not in existing:
                item = dict(group)
                item["created_at"] = self._now()
                item["source"] = "phase193_default_seed"
                groups.append(item)
        state["project_groups"] = groups
        state.setdefault("repo_links", [])
        state.setdefault("conversation_links", [])
        state.setdefault("work_runs", [])
        return state

    def _match_group(self, text: str, groups: List[Dict[str, Any]]) -> Dict[str, Any] | None:
        norm = self._norm(text)
        best = None
        best_score = 0
        for group in groups:
            score = 0
            for alias in group.get("aliases", []):
                if alias and alias in norm:
                    score += len(alias.split()) + 1
            if score > best_score:
                best = group
                best_score = score
        return best

    def _front(self, text: str) -> str:
        n = self._norm(text)
        if any(x in n for x in ["website", "site", "web"]):
            return "website"
        if any(x in n for x in ["studio", "estudio", "creator"]):
            return "studio"
        if any(x in n for x in ["backend", "api", "server"]):
            return "backend"
        if any(x in n for x in ["android", "apk", "mobile", "telemovel"]):
            return "mobile"
        if any(x in n for x in ["windows", "exe", "desktop", "pc"]):
            return "desktop"
        if any(x in n for x in ["admin", "oner"]):
            return "admin"
        return "unknown"

    def _slug(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", self._norm(value)).strip("_")

    def _norm(self, value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip().lower())


real_work_fast_path_service = RealWorkFastPathService()
