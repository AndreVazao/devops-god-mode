from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.mobile_approval_cockpit_v2_service import mobile_approval_cockpit_v2_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
LAB_REGISTRY_FILE = DATA_DIR / "external_skills_lab_registry.json"
LAB_REGISTRY_STORE = AtomicJsonStore(
    LAB_REGISTRY_FILE,
    default_factory=lambda: {"version": 1, "labs": [], "repo_assessments": [], "decisions": [], "reuse_plans": [], "lab_creation_plans": [], "evolution_cards": []},
)

DEFAULT_SKILLS_LABS = [
    ("openai_skills_lab", "AndreVazao/godmode-openai-skills-lab", "openai/skills", "core_agent_skills", "high", "active_lab"),
    ("anthropic_skills_lab", "AndreVazao/godmode-anthropic-skills-lab", "anthropics/skills", "core_agent_skills", "high", "active_lab"),
    ("vercel_skills_cli_lab", "AndreVazao/godmode-vercel-skills-cli-lab", "vercel-labs/skills", "skills_cli_installer", "high", "active_lab"),
    ("android_skills_lab", "AndreVazao/godmode-android-skills-lab", "android/skills", "android_apk", "high", "active_lab"),
    ("gemini_skills_lab", "AndreVazao/godmode-gemini-skills-lab", "google-gemini/gemini-skills", "provider_adapter", "high", "active_lab"),
    ("cloudflare_skills_lab", "AndreVazao/godmode-cloudflare-skills-lab", "cloudflare/skills", "edge_deploy_mcp", "medium", "active_lab"),
    ("awesome_copilot_lab", "AndreVazao/godmode-awesome-copilot-lab", "github/awesome-copilot", "github_agents_workflows", "high", "active_lab"),
    ("browser_act_skills_lab", "AndreVazao/godmode-browser-act-skills-lab", "browser-act/skills", "browser_automation_quarantine", "medium", "quarantine_lab"),
    ("google_cloud_skills_lab", "AndreVazao/godmode-google-cloud-skills-lab", "google/skills", "cloud_optional", "medium", "active_lab"),
    ("heygen_skills_lab", "AndreVazao/godmode-heygen-skills-lab", "heygen-com/skills", "content_video_vertical", "low", "vertical_lab"),
]

CATEGORY_RULES = {
    "core_agent_skills": ["skill", "agent", "codex", "claude", "openai", "anthropic", "prompt"],
    "skills_cli_installer": ["cli", "install", "registry", "skill installer", "multi-agent"],
    "android_apk": ["android", "apk", "gradle", "kotlin", "mobile"],
    "provider_adapter": ["gemini", "provider", "llm", "api", "multimodal", "live"],
    "edge_deploy_mcp": ["cloudflare", "worker", "mcp", "edge", "tunnel", "durable"],
    "github_agents_workflows": ["github", "copilot", "workflow", "actions", "pull request", "agent"],
    "browser_automation_quarantine": ["browser", "automation", "captcha", "stealth", "scrape", "login", "session"],
    "cloud_optional": ["google cloud", "firebase", "cloud run", "bigquery", "gke", "cloud sql"],
    "content_video_vertical": ["video", "avatar", "heygen", "media", "content", "tts"],
}

RISK_RULES = {
    "high_risk": ["captcha", "stealth", "password", "token", "cookie", "scrape", "spyware", "credential", "payment", "paid api"],
    "medium_risk": ["deploy", "cloud", "browser", "session", "api key", "external service"],
    "low_risk": ["docs", "template", "example", "readme", "instruction", "skill"],
}


class ExternalSkillsLabRegistryService:
    SERVICE_ID = "external_skills_lab_registry"
    VERSION = "phase_199_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = self._state_with_defaults()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(LAB_REGISTRY_FILE),
            "lab_count": len(state.get("labs", [])),
            "repo_assessment_count": len(state.get("repo_assessments", [])),
            "decision_count": len(state.get("decisions", [])),
            "reuse_plan_count": len(state.get("reuse_plans", [])),
            "lab_creation_plan_count": len(state.get("lab_creation_plans", [])),
            "controlled_self_evolution_ready": True,
            "auto_catalog_new_repos_ready": True,
            "can_apply_code_without_gate": False,
            "can_create_lab_without_gate": False,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "God Mode can evaluate external repos, decide if they are useful, prepare labs/workflows and propose self-evolution, but cannot apply/merge/release risky changes without gates and Oner approval.",
                "self_evolution_allowed": ["catalog repos", "rank usefulness", "create lab creation plan", "generate upstream import workflow", "prepare native reuse plan", "open PR through approved GitHub flow", "validate with Actions", "update memory after merge"],
                "self_evolution_blocked": ["direct merge without approval", "release without approval", "store secrets", "blind code copy", "copy incompatible license", "use quarantined browser automation without explicit gate"],
                "repo_catalog_decisions": ["lab_now", "reference_only", "quarantine_lab", "vertical_lab", "ignore"],
                "reuse_modes": ["reference", "adapt_native", "copy_with_review", "quarantine_review", "reject"],
            },
        }

    def seed_defaults(self) -> Dict[str, Any]:
        state = self._state_with_defaults(force_persist=True)
        return {"ok": True, "mode": "external_skills_lab_seed", "labs": state.get("labs", [])}

    def list_labs(self, category: str | None = None) -> Dict[str, Any]:
        labs = self._state_with_defaults().get("labs", [])
        if category:
            labs = [lab for lab in labs if lab.get("category") == category]
        return {"ok": True, "mode": "external_skills_lab_list", "count": len(labs), "labs": labs}

    def assess_external_repo(self, repo_full_name: str, description: str = "", operator_goal: str = "", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        text = f"{repo_full_name} {description} {operator_goal}".lower()
        category_scores = []
        for category, words in CATEGORY_RULES.items():
            hits = [word for word in words if word in text]
            score = len(hits) * 3
            category_scores.append({"category": category, "score": score, "hits": hits})
        category_scores.sort(key=lambda item: item["score"], reverse=True)
        best = category_scores[0] if category_scores else {"category": "unknown", "score": 0, "hits": []}
        risk = self._risk(text)
        decision = self._catalog_decision(best, risk)
        lab_repo = self._suggest_lab_repo_name(repo_full_name)
        assessment = {
            "assessment_id": f"external-repo-assessment-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "repo_full_name": repo_full_name.strip(),
            "description": description[:1000],
            "operator_goal": operator_goal[:1000],
            "best_category": best.get("category"),
            "category_scores": category_scores,
            "risk": risk,
            "recommended_catalog_decision": decision,
            "suggested_lab_repo_full_name": lab_repo,
            "reason": self._reason(best, risk, decision),
            "can_create_lab_directly": False,
            "requires_oner_approval": decision in {"lab_now", "quarantine_lab", "vertical_lab"},
            "blocked_until_review": risk == "high_risk",
        }
        self._store("repo_assessments", assessment)
        creation_plan = None
        if decision in {"lab_now", "quarantine_lab", "vertical_lab"}:
            creation_plan = self.create_lab_creation_plan(assessment["assessment_id"], tenant_id=tenant_id)
        card = self._create_assessment_card(assessment, creation_plan, tenant_id=tenant_id)
        return {"ok": True, "mode": "external_repo_assessment", "assessment": assessment, "lab_creation_plan": creation_plan, "review_card": card}

    def catalog_external_repos(self, repositories: List[Dict[str, Any]], operator_goal: str = "", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        results = []
        for repo in repositories[:100]:
            full_name = str(repo.get("repository_full_name") or repo.get("full_name") or repo.get("repo_full_name") or "").strip()
            if not full_name or "/" not in full_name:
                continue
            description = str(repo.get("description") or repo.get("summary") or "")
            results.append(self.assess_external_repo(full_name, description=description, operator_goal=operator_goal, tenant_id=tenant_id)["assessment"])
        return {"ok": True, "mode": "external_repo_catalog_batch", "count": len(results), "assessments": results}

    def create_lab_creation_plan(self, assessment_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        assessment = self._find("repo_assessments", "assessment_id", assessment_id)
        if not assessment:
            return {"ok": False, "mode": "lab_creation_plan", "error": "assessment_not_found", "assessment_id": assessment_id}
        upstream = assessment["repo_full_name"]
        lab_repo = assessment["suggested_lab_repo_full_name"]
        decision = assessment["recommended_catalog_decision"]
        branch = "main"
        plan = {
            "lab_creation_plan_id": f"lab-creation-plan-{uuid4().hex[:12]}",
            "assessment_id": assessment_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "upstream_repo_full_name": upstream,
            "suggested_lab_repo_full_name": lab_repo,
            "recommended_catalog_decision": decision,
            "risk": assessment.get("risk"),
            "steps": [
                "Create empty private lab repo under AndreVazao if it does not exist.",
                "Add README contract: upstream, purpose, allowed uses, blocked uses.",
                "Add .github/workflows/import-upstream.yml to clone upstream into /upstream/.",
                "Run workflow manually to materialize snapshot.",
                "Read docs/UPSTREAM_SNAPSHOT.json and decide native reuse candidates.",
                "If useful, create PR in devops-god-mode with adapted native code, not blind dependency.",
                "Run all checks before merge and update AndreOS memory.",
            ],
            "readme_template": self._readme_template(upstream, lab_repo, assessment),
            "workflow_template": self._workflow_template(upstream, branch),
            "can_execute_without_gate": False,
            "requires_oner_approval": True,
        }
        self._store("lab_creation_plans", plan)
        return {"ok": True, "mode": "lab_creation_plan", "lab_creation_plan": plan}

    def decide_reuse(self, operator_request: str, target_project: str = "GOD_MODE", target_area: str = "auto", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        labs = self._state_with_defaults().get("labs", [])
        ranked = sorted([self._score_lab(lab, operator_request, target_area) for lab in labs], key=lambda item: item["score"], reverse=True)
        top = [item for item in ranked if item["score"] > 0][:5]
        decision = {
            "decision_id": f"skills-lab-decision-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "operator_request": operator_request[:1200],
            "target_project": target_project,
            "target_area": target_area,
            "top_candidates": top,
            "recommended_mode": self._recommended_mode(top),
            "can_apply_directly": False,
            "requires_pr": True,
            "requires_tests": True,
            "requires_oner_approval_for": ["merge", "release", "deploy", "paid API", "browser automation", "credential handling"],
        }
        self._store("decisions", decision)
        plan = self.create_reuse_plan(decision["decision_id"], tenant_id=tenant_id)
        card = self._create_evolution_card(decision, plan, tenant_id=tenant_id)
        return {"ok": True, "mode": "external_skills_lab_reuse_decision", "decision": decision, "reuse_plan": plan, "evolution_card": card}

    def create_reuse_plan(self, decision_id: str, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        decision = self._find("decisions", "decision_id", decision_id)
        if not decision:
            return {"ok": False, "mode": "external_skills_lab_reuse_plan", "error": "decision_not_found", "decision_id": decision_id}
        plan = {
            "reuse_plan_id": f"skills-reuse-plan-{uuid4().hex[:12]}",
            "decision_id": decision_id,
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "target_project": decision.get("target_project"),
            "candidate_count": len(decision.get("top_candidates", [])),
            "recommended_mode": decision.get("recommended_mode"),
            "steps": [
                "Search existing God Mode modules before adding anything new.",
                "Inspect selected lab README/SKILL.md/snapshot evidence.",
                "Classify reuse mode: reference, adapt_native, copy_with_review, quarantine_review or reject.",
                "Prepare minimal native implementation plan in God Mode style.",
                "Apply only through approved GitHub action executor / PR flow.",
                "Run Phase smoke + Universal + Android + Windows checks.",
                "Update AndreOS memory after merge.",
            ],
            "gates": {
                "destructive_actions": "blocked_without_oner_approval",
                "merge": "requires_oner_approval_and_green_checks",
                "release": "requires_oner_approval",
                "deploy_paid_cloud_or_video": "requires_oner_approval",
                "browser_automation": "requires_high_risk_gate",
                "credentials": "never_store_raw_secrets",
            },
            "ready_for_patch_planning": bool(decision.get("top_candidates")),
            "can_apply_directly": False,
        }
        self._store("reuse_plans", plan)
        return {"ok": True, "mode": "external_skills_lab_reuse_plan", "reuse_plan": plan}

    def dashboard(self) -> Dict[str, Any]:
        state = self._state_with_defaults()
        return {"ok": True, "mode": "external_skills_lab_registry_dashboard", "status": self.status(), "policy": self.policy(), "labs": state.get("labs", []), "repo_assessments": state.get("repo_assessments", [])[-100:], "recent_decisions": state.get("decisions", [])[-50:], "reuse_plans": state.get("reuse_plans", [])[-50:], "lab_creation_plans": state.get("lab_creation_plans", [])[-50:], "evolution_cards": state.get("evolution_cards", [])[-50:]}

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _state_with_defaults(self, force_persist: bool = False) -> Dict[str, Any]:
        state = LAB_REGISTRY_STORE.load()
        existing = {item.get("lab_id") for item in state.get("labs", [])}
        labs = list(state.get("labs", []))
        for lab_id, repo, upstream, category, priority, status in DEFAULT_SKILLS_LABS:
            if lab_id not in existing:
                labs.append({"lab_id": lab_id, "repo_full_name": repo, "upstream": upstream, "category": category, "priority": priority, "status": status, "created_at": self._now(), "source": "phase199_default_registry", "allowed_uses": CATEGORY_RULES.get(category, []), "blocked_uses": self._blocked_for_status(status, category)})
        state["labs"] = labs
        for key in ["repo_assessments", "decisions", "reuse_plans", "lab_creation_plans", "evolution_cards"]:
            state.setdefault(key, [])
        if force_persist:
            LAB_REGISTRY_STORE.update(lambda _state: state)
        return state

    def _risk(self, text: str) -> str:
        if any(word in text for word in RISK_RULES["high_risk"]):
            return "high_risk"
        if any(word in text for word in RISK_RULES["medium_risk"]):
            return "medium_risk"
        return "low_risk"

    def _catalog_decision(self, best: Dict[str, Any], risk: str) -> str:
        if best.get("score", 0) <= 0:
            return "ignore"
        if best.get("category") == "browser_automation_quarantine" or risk == "high_risk":
            return "quarantine_lab"
        if best.get("category") == "content_video_vertical":
            return "vertical_lab"
        if best.get("score", 0) >= 3:
            return "lab_now"
        return "reference_only"

    def _reason(self, best: Dict[str, Any], risk: str, decision: str) -> str:
        return f"category={best.get('category')} hits={','.join(best.get('hits', [])) or 'none'} risk={risk} decision={decision}"

    def _suggest_lab_repo_name(self, repo_full_name: str) -> str:
        owner, name = repo_full_name.split("/", 1)
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        return f"AndreVazao/godmode-{slug}-lab"

    def _readme_template(self, upstream: str, lab_repo: str, assessment: Dict[str, Any]) -> str:
        return f"# {lab_repo.split('/')[-1]}\n\nLaboratório privado do God Mode para estudar `{upstream}`.\n\n## Upstream\n\n- Repo: `{upstream}`\n- Papel: {assessment.get('best_category')}\n- Risco: {assessment.get('risk')}\n\n## Política\n\n- Lab/referência, não dependência central.\n- Não guardar tokens, passwords, cookies, API keys ou segredos.\n- Importação para o core exige PR, gates, validação e aprovação do Oner quando aplicável.\n"

    def _workflow_template(self, upstream: str, branch: str = "main") -> str:
        return f"name: Import upstream snapshot\n\non:\n  workflow_dispatch:\n\npermissions:\n  contents: write\n\njobs:\n  import-upstream:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          persist-credentials: true\n      - run: |\n          set -euo pipefail\n          rm -rf upstream\n          git clone --depth 1 --branch {branch} https://github.com/{upstream}.git upstream\n          rm -rf upstream/.git\n          mkdir -p docs\n          python - <<'PY'\n          import json, time\n          from pathlib import Path\n          root=Path('upstream')\n          files=[str(p) for p in root.rglob('*') if p.is_file()]\n          skills=[str(p.parent) for p in root.rglob('SKILL.md')]\n          Path('docs/UPSTREAM_SNAPSHOT.json').write_text(json.dumps({{'upstream':'{upstream}','imported_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'file_count':len(files),'skill_count':len(skills),'skills':skills[:500],'policy':'lab only; no secrets'}}, indent=2), encoding='utf-8')\n          PY\n      - run: |\n          git config user.name godmode-lab-bot\n          git config user.email actions@github.com\n          git add upstream docs/UPSTREAM_SNAPSHOT.json\n          if git diff --cached --quiet; then echo 'No changes'; else git commit -m 'Import upstream snapshot' && git push; fi\n"

    def _score_lab(self, lab: Dict[str, Any], request: str, target_area: str) -> Dict[str, Any]:
        text = f"{request} {target_area}".lower()
        score = 0
        hits = []
        for word in CATEGORY_RULES.get(lab.get("category"), []):
            if word in text:
                score += 3
                hits.append(word)
        if lab.get("priority") == "high":
            score += 1
        mode = "quarantine_review" if lab.get("status") == "quarantine_lab" and score > 0 else "adapt_native" if score >= 4 else "reference" if score > 0 else "ignore"
        return {"lab_id": lab.get("lab_id"), "repo_full_name": lab.get("repo_full_name"), "upstream": lab.get("upstream"), "category": lab.get("category"), "status": lab.get("status"), "score": score, "reasons": hits, "suggested_reuse_mode": mode, "blocked_uses": lab.get("blocked_uses", [])}

    def _recommended_mode(self, top: List[Dict[str, Any]]) -> str:
        if not top:
            return "no_lab_match_use_native"
        if any(item.get("suggested_reuse_mode") == "quarantine_review" for item in top[:2]):
            return "quarantine_review_then_native_adapter"
        if top[0].get("score", 0) >= 6:
            return "adapt_native"
        return "reference_then_native_design"

    def _blocked_for_status(self, status: str, category: str) -> List[str]:
        blocked = ["secret import", "blind code copy", "core dependency without PR"]
        if status == "quarantine_lab" or category == "browser_automation_quarantine":
            blocked += ["stealth automation", "captcha bypass", "session reuse without approval", "private chat scrape"]
        if category in {"cloud_optional", "edge_deploy_mcp", "content_video_vertical"}:
            blocked += ["paid action without Oner approval", "deploy without Oner approval"]
        return blocked

    def _create_assessment_card(self, assessment: Dict[str, Any], creation_plan: Dict[str, Any] | None, tenant_id: str) -> Dict[str, Any]:
        result = mobile_approval_cockpit_v2_service.create_card(
            title=f"Repo externa avaliada: {assessment.get('repo_full_name')}",
            body=f"Decisão sugerida: {assessment.get('recommended_catalog_decision')} | categoria={assessment.get('best_category')} | risco={assessment.get('risk')}. God Mode pode preparar lab/workflow, mas criação/aplicação continua gated.",
            card_type="external_repo_catalog_decision",
            project_id="GOD_MODE",
            tenant_id=tenant_id,
            priority="high" if assessment.get("risk") == "high_risk" else "normal",
            requires_approval=False,
            actions=[{"action_id": "review-external-repo", "label": "Rever repo", "decision": "review"}],
            source_ref={"type": "external_repo_assessment", "assessment_id": assessment.get("assessment_id"), "lab_creation_plan_id": (creation_plan or {}).get("lab_creation_plan", {}).get("lab_creation_plan_id")},
            metadata={"decision": assessment.get("recommended_catalog_decision"), "risk": assessment.get("risk"), "can_create_lab_directly": False},
        )
        card = result.get("card")
        if card:
            self._store("evolution_cards", card)
        return result

    def _create_evolution_card(self, decision: Dict[str, Any], plan: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        result = mobile_approval_cockpit_v2_service.create_card(
            title="Plano de evolução controlada pronto",
            body=f"Pedido: {decision.get('operator_request', '')[:220]} | modo={decision.get('recommended_mode')} | candidatos={len(decision.get('top_candidates', []))}. Patch/PR/merge continuam gated.",
            card_type="controlled_self_evolution_plan",
            project_id=decision.get("target_project", "GOD_MODE"),
            tenant_id=tenant_id,
            priority="normal",
            requires_approval=False,
            actions=[{"action_id": "review-evolution-plan", "label": "Rever plano", "decision": "review"}],
            source_ref={"type": "external_skills_lab_decision", "decision_id": decision.get("decision_id"), "reuse_plan_id": plan.get("reuse_plan", {}).get("reuse_plan_id")},
            metadata={"recommended_mode": decision.get("recommended_mode"), "can_apply_directly": False},
        )
        card = result.get("card")
        if card:
            self._store("evolution_cards", card)
        return result

    def _find(self, bucket: str, key: str, value: str) -> Dict[str, Any] | None:
        return next((item for item in LAB_REGISTRY_STORE.load().get(bucket, []) if item.get(key) == value), None)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1000:]
            return state
        LAB_REGISTRY_STORE.update(mutate)


external_skills_lab_registry_service = ExternalSkillsLabRegistryService()
