from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.external_skills_lab_registry_service import external_skills_lab_registry_service
from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
SNAPSHOT_READER_FILE = DATA_DIR / "external_lab_snapshot_reader.json"
SNAPSHOT_READER_STORE = AtomicJsonStore(
    SNAPSHOT_READER_FILE,
    default_factory=lambda: {
        "version": 1,
        "snapshot_imports": [],
        "native_skill_candidates": [],
        "candidate_plans": [],
        "review_cards": [],
    },
)

DOMAIN_RULES: dict[str, list[str]] = {
    "god_mode_core": ["agent", "skill", "memory", "orchestration", "workflow", "planner", "router", "tool"],
    "android_mobile": ["android", "apk", "mobile", "kotlin", "gradle", "overlay", "accessibility"],
    "provider_router": ["provider", "gemini", "openai", "claude", "llm", "live", "multimodal"],
    "cloud_deploy": ["cloud", "deploy", "worker", "run", "firebase", "cloudflare", "vercel", "edge", "mcp"],
    "verbaforge_content": ["video", "avatar", "tts", "media", "content", "youtube", "shorts", "social"],
    "github_workflow": ["github", "copilot", "actions", "pull request", "repo", "ci", "workflow"],
    "browser_quarantine": ["browser", "captcha", "stealth", "session", "login", "scrape", "cookie"],
}

RISK_WORDS: dict[str, list[str]] = {
    "high": ["password", "token", "cookie", "secret", "captcha", "stealth", "credential", "session reuse", "payment", "paid"],
    "medium": ["browser", "deploy", "cloud", "api key", "external api", "billing", "login", "oauth"],
    "low": ["readme", "docs", "skill", "template", "example", "workflow"],
}


class ExternalLabSnapshotReaderService:
    SERVICE_ID = "external_lab_snapshot_reader"
    VERSION = "phase_200_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = SNAPSHOT_READER_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(SNAPSHOT_READER_FILE),
            "snapshot_import_count": len(state.get("snapshot_imports", [])),
            "native_skill_candidate_count": len(state.get("native_skill_candidates", [])),
            "candidate_plan_count": len(state.get("candidate_plans", [])),
            "review_card_count": len(state.get("review_cards", [])),
            "can_apply_candidate_without_gate": False,
            "can_import_raw_lab_code_without_review": False,
            "requires_actions_validation_before_merge": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Lab snapshots are evidence for native God Mode planning, not automatic dependencies.",
                "allowed": [
                    "read sanitized docs/UPSTREAM_SNAPSHOT.json content",
                    "index SKILL.md paths and related metadata",
                    "propose native_skill_candidate records",
                    "create reuse plans and review cards",
                    "prepare PR plans through gated flow",
                ],
                "blocked": [
                    "blind import of upstream code",
                    "storing tokens/passwords/cookies/API keys",
                    "browser automation against private sessions without explicit high-risk gate",
                    "deploying paid cloud/video/API actions without Oner approval",
                    "merge/release without green Actions and Oner approval",
                ],
                "candidate_domains": list(DOMAIN_RULES.keys()),
                "reuse_modes": ["reference", "adapt_native", "quarantine_review", "reject"],
            },
        }

    def ingest_snapshot_text(
        self,
        lab_id: str,
        lab_repo_full_name: str,
        snapshot_text: str,
        operator_goal: str = "",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        snapshot = self._parse_snapshot(snapshot_text)
        if not snapshot.get("ok"):
            return snapshot
        return self.ingest_snapshot(
            lab_id=lab_id,
            lab_repo_full_name=lab_repo_full_name,
            snapshot=snapshot["snapshot"],
            operator_goal=operator_goal,
            tenant_id=tenant_id,
        )

    def ingest_snapshot(
        self,
        lab_id: str,
        lab_repo_full_name: str,
        snapshot: Dict[str, Any],
        operator_goal: str = "",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        lab_id = (lab_id or self._slug(lab_repo_full_name)).strip()
        lab_repo_full_name = lab_repo_full_name.strip()
        skill_paths = self._extract_skill_paths(snapshot)
        imported = {
            "snapshot_import_id": f"lab-snapshot-import-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "lab_id": lab_id,
            "lab_repo_full_name": lab_repo_full_name,
            "upstream": str(snapshot.get("upstream") or snapshot.get("repo") or ""),
            "imported_at": str(snapshot.get("imported_at") or snapshot.get("generated_at") or ""),
            "file_count": int(snapshot.get("file_count") or len(snapshot.get("files", [])) or 0),
            "skill_count": int(snapshot.get("skill_count") or len(skill_paths)),
            "skill_paths": skill_paths[:500],
            "operator_goal": operator_goal[:1000],
            "source_policy": "lab snapshot only; no secrets; no raw code execution",
        }
        candidates = [self._candidate_from_path(imported, path, operator_goal, tenant_id) for path in skill_paths[:200]]
        candidates = [candidate for candidate in candidates if candidate.get("confidence", 0) > 0]
        if not candidates and imported["upstream"]:
            candidates = [self._candidate_from_path(imported, imported["upstream"], operator_goal, tenant_id)]
        candidates.sort(key=lambda item: (item.get("confidence", 0), -len(item.get("risk_flags", []))), reverse=True)
        self._store("snapshot_imports", imported)
        for candidate in candidates:
            self._store("native_skill_candidates", candidate)
        card = self._create_review_card(imported, candidates, tenant_id)
        return {
            "ok": True,
            "mode": "external_lab_snapshot_ingest",
            "snapshot_import": imported,
            "native_skill_candidates": candidates,
            "review_card": card,
        }

    def generate_candidates_from_registry(self, operator_goal: str = "", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        labs = external_skills_lab_registry_service.list_labs().get("labs", [])
        generated: List[Dict[str, Any]] = []
        for lab in labs:
            pseudo_snapshot = {
                "upstream": lab.get("upstream"),
                "skill_count": 0,
                "skills": [lab.get("upstream", ""), lab.get("category", "")],
                "policy": "registry seed fallback; run Import upstream skills snapshot in lab for real paths",
            }
            result = self.ingest_snapshot(
                lab_id=str(lab.get("lab_id")),
                lab_repo_full_name=str(lab.get("repo_full_name")),
                snapshot=pseudo_snapshot,
                operator_goal=operator_goal,
                tenant_id=tenant_id,
            )
            generated.extend(result.get("native_skill_candidates", []))
        return {"ok": True, "mode": "registry_seed_candidate_generation", "count": len(generated), "native_skill_candidates": generated}

    def list_candidates(self, domain: str | None = None, risk: str | None = None, limit: int = 100) -> Dict[str, Any]:
        limit = max(1, min(int(limit), 500))
        candidates = list(SNAPSHOT_READER_STORE.load().get("native_skill_candidates", []))
        if domain:
            candidates = [item for item in candidates if item.get("target_domain") == domain]
        if risk:
            candidates = [item for item in candidates if item.get("risk") == risk]
        candidates.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return {"ok": True, "mode": "native_skill_candidate_list", "count": len(candidates[:limit]), "native_skill_candidates": candidates[:limit]}

    def create_candidate_plan(self, candidate_id: str, target_project: str = "GOD_MODE", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        candidate = self._find("native_skill_candidates", "candidate_id", candidate_id)
        if not candidate:
            return {"ok": False, "mode": "native_skill_candidate_plan", "error": "candidate_not_found", "candidate_id": candidate_id}
        steps = [
            "Search module registry before creating or changing modules.",
            "Inspect lab README/SKILL.md/snapshot evidence manually when available.",
            "Design native God Mode implementation; do not add lab as central dependency.",
            "Prepare branch and PR through approved GitHub flow.",
            "Run Phase 200 smoke plus Universal, Android and Windows checks.",
            "Merge only after green checks and explicit Oner approval.",
            "Update AndreOS memory after merge.",
        ]
        if candidate.get("risk") == "high_risk":
            steps.insert(1, "Run high-risk quarantine review before any implementation plan.")
        plan = {
            "candidate_plan_id": f"candidate-plan-{uuid4().hex[:12]}",
            "candidate_id": candidate_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "target_project": target_project,
            "candidate": candidate,
            "recommended_reuse_mode": candidate.get("reuse_mode"),
            "steps": steps,
            "gates": {
                "apply_code": "requires_PR",
                "merge": "requires_green_actions_and_oner_approval",
                "release": "requires_oner_approval",
                "browser_or_credentials": "blocked_without_explicit_high_risk_gate",
                "paid_cloud_video_api": "blocked_without_oner_approval",
            },
            "can_apply_directly": False,
        }
        self._store("candidate_plans", plan)
        return {"ok": True, "mode": "native_skill_candidate_plan", "candidate_plan": plan}

    def dashboard(self) -> Dict[str, Any]:
        state = SNAPSHOT_READER_STORE.load()
        return {
            "ok": True,
            "mode": "external_lab_snapshot_reader_dashboard",
            "status": self.status(),
            "policy": self.policy(),
            "snapshot_imports": state.get("snapshot_imports", [])[-100:],
            "native_skill_candidates": state.get("native_skill_candidates", [])[-200:],
            "candidate_plans": state.get("candidate_plans", [])[-100:],
            "review_cards": state.get("review_cards", [])[-100:],
        }

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _parse_snapshot(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"ok": False, "mode": "snapshot_parse", "error": "snapshot_text_required"}
        if self._looks_sensitive(text):
            return {"ok": False, "mode": "snapshot_parse", "error": "snapshot_contains_possible_secret", "redacted": True}
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            return {"ok": False, "mode": "snapshot_parse", "error": "invalid_json", "detail": str(exc)}
        if not isinstance(parsed, dict):
            return {"ok": False, "mode": "snapshot_parse", "error": "snapshot_must_be_json_object"}
        return {"ok": True, "mode": "snapshot_parse", "snapshot": parsed}

    def _extract_skill_paths(self, snapshot: Dict[str, Any]) -> List[str]:
        raw = snapshot.get("skills") or snapshot.get("skill_paths") or []
        if isinstance(raw, str):
            raw = [raw]
        paths: List[str] = []
        for item in raw:
            text = str(item).strip()
            if not text:
                continue
            paths.append(text[:500])
        files = snapshot.get("files") or []
        if isinstance(files, list):
            for item in files:
                text = str(item).strip()
                if "SKILL.md" in text and text not in paths:
                    paths.append(text[:500])
        return paths[:500]

    def _candidate_from_path(self, imported: Dict[str, Any], path: str, operator_goal: str, tenant_id: str) -> Dict[str, Any]:
        text = f"{path} {imported.get('upstream')} {operator_goal}".lower()
        domain, confidence, hits = self._classify_domain(text)
        risk, risk_flags = self._risk(text)
        reuse_mode = self._reuse_mode(domain, risk, confidence)
        return {
            "candidate_id": f"native-skill-candidate-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "snapshot_import_id": imported.get("snapshot_import_id"),
            "lab_id": imported.get("lab_id"),
            "lab_repo_full_name": imported.get("lab_repo_full_name"),
            "upstream": imported.get("upstream"),
            "source_path": path,
            "candidate_name": self._candidate_name(path),
            "target_domain": domain,
            "confidence": confidence,
            "matched_terms": hits,
            "risk": risk,
            "risk_flags": risk_flags,
            "reuse_mode": reuse_mode,
            "intended_use": self._intended_use(domain),
            "can_apply_directly": False,
            "requires_pr": True,
            "requires_tests": True,
            "requires_oner_approval_for": self._approval_scope(domain, risk),
        }

    def _classify_domain(self, text: str) -> tuple[str, int, List[str]]:
        best_domain = "god_mode_core"
        best_score = 0
        best_hits: List[str] = []
        for domain, words in DOMAIN_RULES.items():
            hits = [word for word in words if word in text]
            score = len(hits) * 3
            if score > best_score:
                best_domain = domain
                best_score = score
                best_hits = hits
        return best_domain, best_score, best_hits

    def _risk(self, text: str) -> tuple[str, List[str]]:
        high = [word for word in RISK_WORDS["high"] if word in text]
        if high:
            return "high_risk", high
        medium = [word for word in RISK_WORDS["medium"] if word in text]
        if medium:
            return "medium_risk", medium
        low = [word for word in RISK_WORDS["low"] if word in text]
        return "low_risk", low

    def _reuse_mode(self, domain: str, risk: str, confidence: int) -> str:
        if risk == "high_risk" or domain == "browser_quarantine":
            return "quarantine_review"
        if confidence >= 6:
            return "adapt_native"
        if confidence > 0:
            return "reference"
        return "reject"

    def _intended_use(self, domain: str) -> str:
        return {
            "god_mode_core": "Improve native orchestration, memory, agent/tool planning and self-evolution patterns.",
            "android_mobile": "Improve Android/APK/mobile cockpit implementation without making labs central dependencies.",
            "provider_router": "Improve provider routing/adapters and multimodal/live provider planning safely.",
            "cloud_deploy": "Plan optional cloud/deploy/MCP patterns with paid/deploy gates.",
            "verbaforge_content": "Feed VerbaForge/media/content capabilities only through vertical gated plans.",
            "github_workflow": "Improve PR/build/workflow hygiene and repo automation through validated Actions.",
            "browser_quarantine": "Keep browser automation evidence quarantined until explicit high-risk review.",
        }.get(domain, "Reference-only native planning.")

    def _approval_scope(self, domain: str, risk: str) -> List[str]:
        scope = ["merge", "release"]
        if risk == "high_risk" or domain == "browser_quarantine":
            scope += ["browser automation", "credential/session handling"]
        if domain in {"cloud_deploy", "verbaforge_content"}:
            scope += ["paid API", "deploy", "billing-sensitive action"]
        return sorted(set(scope))

    def _candidate_name(self, path: str) -> str:
        name = path.rstrip("/").split("/")[-2:] if "/" in path else [path]
        label = " / ".join(name).replace("SKILL.md", "skill").strip(" /-")
        return re.sub(r"\s+", " ", label)[:120] or "native skill candidate"

    def _slug(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "external_lab"

    def _looks_sensitive(self, text: str) -> bool:
        return bool(re.search(r"(?i)(api[_-]?key|secret|password|token|cookie)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}", text))

    def _create_review_card(self, imported: Dict[str, Any], candidates: List[Dict[str, Any]], tenant_id: str) -> Dict[str, Any]:
        top = candidates[0] if candidates else {}
        result = mobile_approval_cockpit_v2_service.create_card(
            title=f"Snapshot lab lido: {imported.get('lab_repo_full_name')}",
            body=f"{len(candidates)} candidatos nativos encontrados. Top: {top.get('candidate_name', 'sem candidato')} | domínio={top.get('target_domain', 'n/a')} | risco={top.get('risk', 'n/a')}. Nada aplica sem PR/gates.",
            card_type="native_skill_candidate_review",
            project_id="GOD_MODE",
            tenant_id=tenant_id,
            priority="high" if any(item.get("risk") == "high_risk" for item in candidates) else "normal",
            requires_approval=False,
            actions=[{"action_id": "review-native-skill-candidates", "label": "Rever candidatos", "decision": "review"}],
            source_ref={"type": "external_lab_snapshot_import", "snapshot_import_id": imported.get("snapshot_import_id")},
            metadata={"candidate_count": len(candidates), "can_apply_directly": False},
        )
        card = result.get("card")
        if card:
            self._store("review_cards", card)
        return result

    def _find(self, bucket: str, key: str, value: str) -> Dict[str, Any] | None:
        return next((item for item in SNAPSHOT_READER_STORE.load().get(bucket, []) if item.get(key) == value), None)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1500:]
            return state
        SNAPSHOT_READER_STORE.update(mutate)


external_lab_snapshot_reader_service = ExternalLabSnapshotReaderService()
