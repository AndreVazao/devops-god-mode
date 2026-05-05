from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.conversation_requirement_ledger_service import conversation_requirement_ledger_service
from app.services.provider_outcome_learning_service import provider_outcome_learning_service
from app.services.smol_godmode_reference_adapter_service import smol_godmode_reference_adapter_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
BROADCAST_FILE = DATA_DIR / "provider_prompt_broadcast_runtime.json"
BROADCAST_STORE = AtomicJsonStore(
    BROADCAST_FILE,
    default_factory=lambda: {"version": 1, "pane_profiles": [], "broadcast_plans": [], "provider_jobs": [], "response_imports": []},
)

SAFE_PROVIDER_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


class ProviderPromptBroadcastRuntimeService:
    """Native multi-provider pane manifest and prompt broadcast runtime.

    This phase does not automate browser input yet. It creates provider pane
    profiles, broadcast plans and response-import contracts. Browser automation
    and credential/session actions remain gated by later runtime proofs.
    """

    SERVICE_ID = "provider_prompt_broadcast_runtime"
    VERSION = "phase_190_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = BROADCAST_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "store_file": str(BROADCAST_FILE),
            "pane_profile_count": len(state.get("pane_profiles", [])),
            "broadcast_plan_count": len(state.get("broadcast_plans", [])),
            "provider_job_count": len(state.get("provider_jobs", [])),
            "response_import_count": len(state.get("response_imports", [])),
            "browser_automation_enabled": False,
            "stores_credentials": False,
            "operator_request_preserved": True,
            "ai_responses_are_not_decisions": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Broadcast keeps the Oner's original request immutable and treats every provider answer as ai_response, not as a decision.",
                "phase_scope": "pane manifests, provider selection, broadcast plans, response import and ledger linkage",
                "blocked": ["store credentials", "store cookies", "browser automation without future gate", "treat provider answer as final decision", "apply scripts without reconciliation"],
                "allowed": ["create pane profile", "select providers", "plan broadcast", "record manual/provider response import", "link response to ledger"],
                "future_gates": ["real browser input", "credential entry", "script apply", "repo write", "deploy", "merge", "release"],
            },
        }

    def default_pane_profile(self, profile_name: str = "default_multi_ai_cockpit") -> Dict[str, Any]:
        manifest = smol_godmode_reference_adapter_service.provider_pane_manifest()
        providers = []
        for index, provider in enumerate(manifest.get("providers", []), start=1):
            providers.append({
                "provider_id": provider["id"],
                "label": provider["label"],
                "kind": provider["kind"],
                "enabled": bool(provider.get("default_enabled")),
                "pane_order": index,
                "ledger_role": provider.get("ledger_role", "ai_response_source"),
                "requires_login_attention": provider["kind"] in {"full_webapp", "local_webapp"},
                "credential_storage": "never_store_in_god_mode",
            })
        profile = {
            "profile_id": f"pane-profile-{uuid4().hex[:12]}",
            "profile_name": profile_name,
            "created_at": self._now(),
            "source_reference": "smol-ai/GodMode UX pattern adapted natively",
            "providers": providers,
            "layout": manifest.get("layout", {}),
            "security": manifest.get("security", {}),
            "status": "ready",
        }
        self._store_pane_profile(profile)
        return {"ok": True, "mode": "provider_pane_profile", "profile": profile}

    def create_pane_profile(self, profile_name: str, providers: List[Dict[str, Any]], layout: Dict[str, Any] | None = None) -> Dict[str, Any]:
        normalized = []
        for index, provider in enumerate(providers, start=1):
            provider_id = self._safe_provider_id(provider.get("provider_id") or provider.get("id") or "")
            if not provider_id:
                return {"ok": False, "mode": "provider_pane_profile", "error": "invalid_provider_id", "provider": provider}
            normalized.append({
                "provider_id": provider_id,
                "label": str(provider.get("label") or provider_id)[:120],
                "kind": str(provider.get("kind") or "full_webapp")[:80],
                "enabled": bool(provider.get("enabled", True)),
                "pane_order": int(provider.get("pane_order") or index),
                "ledger_role": str(provider.get("ledger_role") or "ai_response_source")[:80],
                "requires_login_attention": bool(provider.get("requires_login_attention", False)),
                "credential_storage": "never_store_in_god_mode",
            })
        profile = {
            "profile_id": f"pane-profile-{uuid4().hex[:12]}",
            "profile_name": str(profile_name or "custom_profile")[:120],
            "created_at": self._now(),
            "providers": sorted(normalized, key=lambda item: item["pane_order"]),
            "layout": layout or {"default_columns": 2, "supports_resize": True, "supports_reorder": True, "supports_provider_toggle": True},
            "security": {"store_credentials": False, "operator_approval_required_for_credential_entry": True},
            "status": "ready",
        }
        self._store_pane_profile(profile)
        return {"ok": True, "mode": "provider_pane_profile", "profile": profile}

    def create_broadcast_plan(
        self,
        operator_request: str,
        project_key: str = "GOD_MODE",
        selected_provider_ids: List[str] | None = None,
        profile_id: str | None = None,
        context_bundle_ref: str | None = None,
        prompt_mode: str = "plain",
        use_prompt_critic: bool = False,
    ) -> Dict[str, Any]:
        if not operator_request or not operator_request.strip():
            return {"ok": False, "mode": "provider_prompt_broadcast_plan", "error": "operator_request_required"}
        profile = self._get_profile(profile_id) or self.default_pane_profile()["profile"]
        selected = self._selected_providers(profile, selected_provider_ids)
        if not selected:
            return {"ok": False, "mode": "provider_prompt_broadcast_plan", "error": "no_enabled_providers_selected"}
        original_request = operator_request.strip()
        improved_prompt = self._prompt_critic(original_request) if use_prompt_critic else original_request
        plan_id = f"broadcast-plan-{uuid4().hex[:12]}"
        jobs = []
        for provider in selected:
            jobs.append({
                "job_id": f"provider-job-{uuid4().hex[:12]}",
                "plan_id": plan_id,
                "provider_id": provider["provider_id"],
                "provider_label": provider["label"],
                "provider_kind": provider["kind"],
                "ledger_role": provider.get("ledger_role", "ai_response_source"),
                "status": "planned_manual_or_future_runtime_dispatch",
                "browser_automation_executed": False,
                "requires_login_attention": provider.get("requires_login_attention", False),
                "created_at": self._now(),
            })
        plan = {
            "plan_id": plan_id,
            "created_at": self._now(),
            "project_key": self._safe_project(project_key),
            "profile_id": profile["profile_id"],
            "context_bundle_ref": context_bundle_ref,
            "prompt_mode": prompt_mode,
            "use_prompt_critic": use_prompt_critic,
            "operator_request_original": original_request,
            "operator_request_fingerprint": self._fingerprint(original_request),
            "broadcast_prompt": improved_prompt,
            "prompt_changes_summary": self._prompt_changes_summary(original_request, improved_prompt),
            "selected_provider_count": len(selected),
            "selected_provider_ids": [item["provider_id"] for item in selected],
            "jobs": jobs,
            "ledger_seed": {
                "operator_request_role": "operator_request",
                "provider_response_role": "ai_response",
                "answers_are_decisions": False,
                "scripts_require_reconciliation": True,
            },
            "status": "planned",
            "browser_automation_executed": False,
        }
        self._store_plan_and_jobs(plan, jobs)
        return {"ok": True, "mode": "provider_prompt_broadcast_plan", "plan": plan}

    def import_provider_response(self, plan_id: str, provider_id: str, response_text: str, source_mode: str = "manual_import") -> Dict[str, Any]:
        plan = self._get_plan(plan_id)
        if plan is None:
            return {"ok": False, "mode": "provider_response_import", "error": "plan_not_found", "plan_id": plan_id}
        provider_id = self._safe_provider_id(provider_id)
        if provider_id not in plan.get("selected_provider_ids", []):
            return {"ok": False, "mode": "provider_response_import", "error": "provider_not_in_plan", "provider_id": provider_id}
        response_text = response_text or ""
        import_item = {
            "response_import_id": f"response-import-{uuid4().hex[:12]}",
            "plan_id": plan_id,
            "project_key": plan.get("project_key"),
            "provider_id": provider_id,
            "source_mode": source_mode,
            "created_at": self._now(),
            "response_fingerprint": self._fingerprint(response_text),
            "response_preview": response_text[:500],
            "response_length": len(response_text),
            "ledger_role": "ai_response",
            "is_decision": False,
            "requires_reconciliation": True,
            "script_block_count": response_text.count("```") // 2,
        }
        ledger_result = conversation_requirement_ledger_service.analyze_messages(
            project_key=plan.get("project_key", "GOD_MODE"),
            source_provider=provider_id,
            source_id=import_item["response_import_id"],
            store=True,
            messages=[
                {"role": "operator", "speaker": "Oner", "provider": "god_mode", "content": plan.get("operator_request_original", "")},
                {"role": "ai", "speaker": provider_id, "provider": provider_id, "content": response_text},
            ],
        )
        import_item["ledger_analysis_id"] = ledger_result.get("analysis", {}).get("analysis_id")
        self._store_response_import(import_item)
        self._mark_job_imported(plan_id, provider_id)
        self._record_provider_outcome(provider_id, plan, import_item)
        return {"ok": True, "mode": "provider_response_import", "response_import": import_item, "ledger_result": ledger_result}

    def compare_responses(self, plan_id: str) -> Dict[str, Any]:
        state = BROADCAST_STORE.load()
        imports = [item for item in state.get("response_imports", []) if item.get("plan_id") == plan_id]
        plan = self._get_plan(plan_id)
        if plan is None:
            return {"ok": False, "mode": "provider_response_compare", "error": "plan_not_found", "plan_id": plan_id}
        comparison = {
            "comparison_id": f"response-compare-{uuid4().hex[:12]}",
            "plan_id": plan_id,
            "created_at": self._now(),
            "provider_count": len(imports),
            "providers_imported": [item["provider_id"] for item in imports],
            "missing_providers": [provider for provider in plan.get("selected_provider_ids", []) if provider not in {item["provider_id"] for item in imports}],
            "script_block_total": sum(item.get("script_block_count", 0) for item in imports),
            "requires_operator_review": True,
            "answers_are_decisions": False,
            "recommended_next_actions": self._comparison_actions(imports, plan),
        }
        return {"ok": True, "mode": "provider_response_compare", "comparison": comparison}

    def list_plans(self, limit: int = 50) -> Dict[str, Any]:
        state = BROADCAST_STORE.load()
        plans = list(reversed(state.get("broadcast_plans", [])))[0:max(1, min(limit, 200))]
        return {"ok": True, "mode": "provider_prompt_broadcast_plan_list", "plan_count": len(plans), "plans": plans}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "default_pane_manifest": smol_godmode_reference_adapter_service.provider_pane_manifest(),
            "plans": self.list_plans(limit=20),
            "routes": {
                "default_pane_profile": "/api/provider-prompt-broadcast-runtime/default-pane-profile",
                "create_pane_profile": "/api/provider-prompt-broadcast-runtime/create-pane-profile",
                "create_broadcast_plan": "/api/provider-prompt-broadcast-runtime/create-broadcast-plan",
                "import_provider_response": "/api/provider-prompt-broadcast-runtime/import-provider-response",
                "compare_responses": "/api/provider-prompt-broadcast-runtime/compare-responses",
            },
        }

    def _store_pane_profile(self, profile: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            profiles = [item for item in state.get("pane_profiles", []) if item.get("profile_name") != profile.get("profile_name")]
            profiles.append(profile)
            state["pane_profiles"] = profiles[-200:]
            return state
        BROADCAST_STORE.update(mutate)

    def _store_plan_and_jobs(self, plan: Dict[str, Any], jobs: List[Dict[str, Any]]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("broadcast_plans", []).append(plan)
            state.setdefault("provider_jobs", []).extend(jobs)
            state["broadcast_plans"] = state["broadcast_plans"][-500:]
            state["provider_jobs"] = state["provider_jobs"][-2000:]
            return state
        BROADCAST_STORE.update(mutate)

    def _store_response_import(self, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("response_imports", []).append(item)
            state["response_imports"] = state["response_imports"][-2000:]
            return state
        BROADCAST_STORE.update(mutate)

    def _mark_job_imported(self, plan_id: str, provider_id: str) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for job in state.get("provider_jobs", []):
                if job.get("plan_id") == plan_id and job.get("provider_id") == provider_id:
                    job["status"] = "response_imported"
                    job["updated_at"] = self._now()
            return state
        BROADCAST_STORE.update(mutate)

    def _get_profile(self, profile_id: str | None) -> Dict[str, Any] | None:
        if not profile_id:
            return None
        state = BROADCAST_STORE.load()
        return next((item for item in state.get("pane_profiles", []) if item.get("profile_id") == profile_id), None)

    def _get_plan(self, plan_id: str) -> Dict[str, Any] | None:
        state = BROADCAST_STORE.load()
        return next((item for item in state.get("broadcast_plans", []) if item.get("plan_id") == plan_id), None)

    def _selected_providers(self, profile: Dict[str, Any], selected_provider_ids: List[str] | None) -> List[Dict[str, Any]]:
        providers = profile.get("providers", [])
        if selected_provider_ids:
            wanted = {self._safe_provider_id(item) for item in selected_provider_ids}
            return [item for item in providers if item.get("provider_id") in wanted]
        return [item for item in providers if item.get("enabled")]

    def _safe_provider_id(self, value: str) -> str:
        value = (value or "").strip().lower()
        return value if SAFE_PROVIDER_RE.match(value) else ""

    def _safe_project(self, project_key: str) -> str:
        return re.sub(r"[^A-Za-z0-9_\-]+", "_", (project_key or "GOD_MODE").strip().upper()).strip("_") or "GOD_MODE"

    def _fingerprint(self, value: str) -> str:
        return hashlib.sha256((value or "").encode("utf-8", errors="ignore")).hexdigest()

    def _prompt_critic(self, original: str) -> str:
        # Deterministic, local-only prompt improvement. It preserves intent and
        # adds God Mode operating constraints without calling external AI.
        additions = [
            "\n\nContexto operacional God Mode:",
            "- Preserva o pedido original do Oner; não alteres a intenção.",
            "- Se deres código, entrega blocos completos e identifica riscos.",
            "- Se propuseres decisão, marca como proposta, não como decisão final.",
            "- Não peças nem exponhas segredos; usa referências quando necessário.",
        ]
        return original.strip() + "".join(additions)

    def _prompt_changes_summary(self, original: str, improved: str) -> str:
        if original == improved:
            return "Prompt critic disabled; original operator request used verbatim."
        return "Prompt critic appended operating constraints while preserving the original operator request verbatim."

    def _comparison_actions(self, imports: List[Dict[str, Any]], plan: Dict[str, Any]) -> List[str]:
        actions = []
        if not imports:
            actions.append("Import provider responses manually or via future browser proof runtime.")
        if any(item.get("script_block_count", 0) for item in imports):
            actions.append("Send extracted scripts to reconciliation before applying to repo.")
        missing = [provider for provider in plan.get("selected_provider_ids", []) if provider not in {item["provider_id"] for item in imports}]
        if missing:
            actions.append(f"Providers missing response import: {', '.join(missing)}")
        actions.append("Operator must choose accepted decision; provider answers are not final decisions.")
        return actions

    def _record_provider_outcome(self, provider_id: str, plan: Dict[str, Any], item: Dict[str, Any]) -> None:
        try:
            provider_outcome_learning_service.record_outcome(
                provider_id=provider_id,
                task_type="prompt_broadcast_response",
                success=True,
                latency_ms=None,
                quality_score=None,
                notes=f"Imported response for {plan.get('plan_id')} length={item.get('response_length')}",
            )
        except Exception:
            # Outcome learning must not break the broadcast ledger path.
            return


provider_prompt_broadcast_runtime_service = ProviderPromptBroadcastRuntimeService()
