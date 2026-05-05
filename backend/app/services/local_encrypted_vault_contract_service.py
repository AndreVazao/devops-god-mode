from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
VAULT_CONTRACT_FILE = DATA_DIR / "local_encrypted_vault_contract.json"
VAULT_CONTRACT_STORE = AtomicJsonStore(
    VAULT_CONTRACT_FILE,
    default_factory=lambda: {
        "version": 1,
        "policy": "local_pc_encrypted_vault_contract_no_secret_values_in_repo_memory_or_logs",
        "projects": [],
        "secret_refs": [],
        "env_intake_reports": [],
        "placement_plans": [],
        "decisions": [],
    },
)

KEY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_\.\-]*)\s*=\s*(.*)\s*$")
SENSITIVE_KEY_HINTS = (
    "KEY", "TOKEN", "SECRET", "PASSWORD", "PASS", "PWD", "COOKIE", "AUTH", "PRIVATE", "SUPABASE", "RENDER", "VERCEL", "DATABASE_URL", "URL",
)
EXAMPLE_HINTS = ("EXAMPLE", "SAMPLE", "DEMO", "PLACEHOLDER", "YOUR_", "CHANGE_ME", "TODO", "XXX", "FAKE", "TEST")
PROVIDER_HINTS = {
    "SUPABASE": ("SUPABASE", "SB_", "DATABASE_URL", "POSTGRES"),
    "VERCEL": ("VERCEL",),
    "RENDER": ("RENDER",),
    "OPENAI": ("OPENAI", "CHATGPT"),
    "ANTHROPIC": ("ANTHROPIC", "CLAUDE"),
    "GOOGLE": ("GOOGLE", "GEMINI", "FIREBASE"),
    "GITHUB": ("GITHUB", "GH_"),
    "STRIPE": ("STRIPE",),
    "PAYPAL": ("PAYPAL",),
}
PROJECT_HINTS = {
    "BARBUDO_STUDIO": ("BARBUDO", "STUDIO"),
    "BARBUDO_WEBSITE": ("BARBUDO", "WEBSITE", "SITE", "NEXT_PUBLIC"),
    "GOD_MODE": ("GOD_MODE", "GODMODE", "DEVOPS"),
}


class LocalEncryptedVaultContractService:
    """Local encrypted vault contract and first credential flow.

    This service intentionally stores only safe metadata and references.
    Real secret values must remain local to the PC encrypted vault implementation.
    """

    SERVICE_ID = "local_encrypted_vault_contract"
    VERSION = "phase_182_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_project_id(self, value: str | None) -> str:
        raw = (value or "UNKNOWN_PROJECT").strip().upper()
        cleaned = re.sub(r"[^A-Z0-9_\-]+", "_", raw).strip("_")
        return cleaned or "UNKNOWN_PROJECT"

    def _fingerprint(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:20]

    def status(self) -> Dict[str, Any]:
        state = VAULT_CONTRACT_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "vault_mode": "contract_only_until_pc_encrypted_store_is_unlocked",
            "store_file": str(VAULT_CONTRACT_FILE),
            "project_count": len(state.get("projects", [])),
            "secret_ref_count": len(state.get("secret_refs", [])),
            "env_intake_report_count": len(state.get("env_intake_reports", [])),
            "placement_plan_count": len(state.get("placement_plans", [])),
            "stores_secret_values": False,
            "github_memory_allowed": "references_only",
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "God Mode may know where a secret belongs, but must not expose/store the secret value in GitHub, docs, memory or logs.",
                "local_pc_vault": {
                    "role": "encrypted value store on the PC",
                    "future_storage": "data/local_vault/*.vault or OS keyring/DPAPI-backed store",
                    "unlock": "operator approval from PC or mobile cockpit",
                    "audit": "redacted secret_ref_id + target only",
                },
                "github_memory": "technical decisions and safe references only",
                "obsidian": "can mirror notes/labels, never values unless user intentionally stores them locally outside cloud sync",
                "blocked": [
                    "commit raw secret values",
                    "store tokens/passwords/cookies in AndreOS memory",
                    "send secrets to external AI as context",
                    "log raw credential values",
                    "auto-deploy secrets without approval gate",
                ],
                "allowed": [
                    "secret reference IDs",
                    "provider/project/environment mapping",
                    "placement plans for where each secret should be injected",
                    "fingerprints for duplicate detection",
                    "example-vs-real classification without exposing values",
                ],
            },
        }

    def register_project(self, project_id: str, repo_full_name: str | None = None, role: str = "app", notes: str | None = None) -> Dict[str, Any]:
        project_id = self._safe_project_id(project_id)
        record = {
            "project_id": project_id,
            "repo_full_name": repo_full_name,
            "role": role,
            "notes": (notes or "")[:1200],
            "updated_at": self._now(),
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            projects = [item for item in state.get("projects", []) if item.get("project_id") != project_id]
            projects.append(record)
            state["projects"] = projects[-200:]
            return state

        VAULT_CONTRACT_STORE.update(mutate)
        return {"ok": True, "mode": "local_vault_project_registered", "project": record}

    def classify_env_text(self, env_text: str, source_name: str = "uploaded_env", project_hint: str | None = None, environment_name: str = "unknown") -> Dict[str, Any]:
        items = []
        ignored = 0
        for line_no, line in enumerate((env_text or "").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                ignored += 1
                continue
            match = KEY_RE.match(line)
            if not match:
                ignored += 1
                continue
            key, value = match.group(1).strip(), match.group(2).strip().strip('"').strip("'")
            items.append(self._classify_item(key=key, value=value, line_no=line_no, project_hint=project_hint, environment_name=environment_name))
        report = {
            "report_id": f"env-intake-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "source_name": source_name[:300],
            "project_hint": self._safe_project_id(project_hint),
            "environment_name": environment_name,
            "item_count": len(items),
            "ignored_line_count": ignored,
            "items": items,
            "safe_summary": self._summary(items),
            "stores_secret_values": False,
        }
        return {"ok": True, "mode": "env_text_classified_without_values", "report": report}

    def intake_env_text(self, env_text: str, source_name: str, project_hint: str | None = None, environment_name: str = "unknown", store_report: bool = True) -> Dict[str, Any]:
        result = self.classify_env_text(env_text=env_text, source_name=source_name, project_hint=project_hint, environment_name=environment_name)
        report = result["report"]
        if store_report:
            self._store_report(report)
            self._store_secret_refs_from_report(report)
        placement = self.build_placement_plan_from_report(report)
        return {"ok": True, "mode": "local_vault_env_intake", "report": report, "placement_plan": placement["plan"]}

    def build_placement_plan_from_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        targets = []
        for item in report.get("items", []):
            if item.get("classification") == "example_value":
                continue
            target_project = item.get("project_guess") or report.get("project_hint") or "UNKNOWN_PROJECT"
            target = {
                "secret_ref_id": item["secret_ref_id"],
                "key": item["key"],
                "provider_guess": item.get("provider_guess"),
                "target_project": target_project,
                "environment_name": report.get("environment_name"),
                "inject_as": item["key"],
                "requires_operator_approval": True,
                "requires_local_vault_value": item.get("requires_local_vault_value", True),
                "placement_status": "planned_not_deployed",
            }
            targets.append(target)
        plan = {
            "placement_plan_id": f"placement-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "source_report_id": report.get("report_id"),
            "target_count": len(targets),
            "targets": targets,
            "blocked_until": ["local_pc_vault_unlocked", "operator_approval", "target_project_confirmed"],
        }
        self._store_placement_plan(plan)
        return {"ok": True, "mode": "local_vault_placement_plan", "plan": plan}

    def first_credential_flow(self, project_id: str = "GOD_MODE", provider: str = "unknown", environment_name: str = "production") -> Dict[str, Any]:
        project_id = self._safe_project_id(project_id)
        return {
            "ok": True,
            "mode": "first_credential_flow_contract",
            "project_id": project_id,
            "provider": provider,
            "environment_name": environment_name,
            "steps": [
                {"step": 1, "label": "Operator uploads or pastes env file/text locally", "secret_values_leave_pc": False},
                {"step": 2, "label": "God Mode classifies keys and detects example vs real", "secret_values_leave_pc": False},
                {"step": 3, "label": "God Mode stores only secret_ref_id/fingerprint/provider/project mapping", "secret_values_leave_pc": False},
                {"step": 4, "label": "Operator confirms target project and environment from phone/PC cockpit", "approval_required": True},
                {"step": 5, "label": "Local encrypted vault stores/uses actual value on PC only", "approval_required": True},
                {"step": 6, "label": "Deploy binding injects secret into selected target without logging value", "approval_required": True},
                {"step": 7, "label": "Audit records redacted secret_ref_id and target", "secret_values_leave_pc": False},
            ],
            "blocked_actions": ["auto deploy without approval", "store raw value in GitHub", "send raw value to external AI"],
        }

    def project_mapping_bootstrap(self) -> Dict[str, Any]:
        projects = [
            self.register_project("GOD_MODE", repo_full_name="AndreVazao/devops-god-mode", role="orchestrator", notes="PC brain + mobile cockpit; owns vault policy and deployment placement logic.")["project"],
            self.register_project("BARBUDO_STUDIO", role="studio_control_app", notes="Studio controls website via API/routes/env bindings. Exact repo can be confirmed later.")["project"],
            self.register_project("BARBUDO_WEBSITE", role="public_website", notes="Website target controlled by Studio; may use Supabase/Vercel style envs depending on current deployment.")["project"],
        ]
        decision = {
            "decision_id": f"vault-decision-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "title": "Barbudo Studio/Website env ownership mapping",
            "summary": "God Mode should remember which env/API refs belong to Studio vs Website and generate placement plans without exposing values.",
            "projects": [p["project_id"] for p in projects],
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("decisions", [])
            state["decisions"].append(decision)
            state["decisions"] = state["decisions"][-100:]
            return state

        VAULT_CONTRACT_STORE.update(mutate)
        return {"ok": True, "mode": "project_mapping_bootstrap", "projects": projects, "decision": decision}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "first_credential_flow": self.first_credential_flow(),
            "project_mapping_hint": {
                "barbudo_studio": "controls website via API/routes/env bindings",
                "barbudo_website": "public site target; may need Supabase/Vercel style envs",
                "god_mode": "orchestrator and local vault owner",
            },
            "env_intake_endpoint": "/api/local-encrypted-vault-contract/intake-env-text",
            "placement_rule": "example values are never deployed; real values require local vault + operator approval.",
        }

    def _classify_item(self, key: str, value: str, line_no: int, project_hint: str | None, environment_name: str) -> Dict[str, Any]:
        upper_key = key.upper()
        upper_value = value.upper()
        provider = self._provider_guess(upper_key, upper_value)
        project_guess = self._project_guess(upper_key, upper_value, project_hint)
        classification = "example_value" if self._looks_example(upper_key, upper_value, value) else "real_candidate"
        sensitivity = "secret_candidate" if self._looks_sensitive(upper_key) else "config_candidate"
        return {
            "line_no": line_no,
            "key": key,
            "secret_ref_id": f"secret-ref-{self._safe_project_id(project_guess)}-{self._fingerprint(key + ':' + value)}",
            "classification": classification,
            "sensitivity": sensitivity,
            "provider_guess": provider,
            "project_guess": project_guess,
            "environment_name": environment_name,
            "value_fingerprint": self._fingerprint(value) if value else None,
            "value_length": len(value),
            "has_value": bool(value),
            "value_preview": self._redacted_preview(value),
            "requires_local_vault_value": classification != "example_value" and sensitivity == "secret_candidate",
            "deploy_allowed_without_confirmation": False,
        }

    def _provider_guess(self, upper_key: str, upper_value: str) -> str:
        haystack = f"{upper_key} {upper_value}"
        for provider, hints in PROVIDER_HINTS.items():
            if any(hint in haystack for hint in hints):
                return provider
        return "UNKNOWN"

    def _project_guess(self, upper_key: str, upper_value: str, project_hint: str | None) -> str:
        if project_hint:
            return self._safe_project_id(project_hint)
        haystack = f"{upper_key} {upper_value}"
        for project, hints in PROJECT_HINTS.items():
            if any(hint in haystack for hint in hints):
                return project
        return "UNKNOWN_PROJECT"

    def _looks_sensitive(self, upper_key: str) -> bool:
        return any(hint in upper_key for hint in SENSITIVE_KEY_HINTS)

    def _looks_example(self, upper_key: str, upper_value: str, original: str) -> bool:
        if not original or original.strip() in {"", "...", "<value>", "<secret>", "changeme"}:
            return True
        haystack = f"{upper_key} {upper_value}"
        if any(hint in haystack for hint in EXAMPLE_HINTS):
            return True
        if upper_value.startswith("SK-EXAMPLE") or "YOUR-" in upper_value:
            return True
        return False

    def _redacted_preview(self, value: str) -> str:
        if not value:
            return ""
        if len(value) <= 6:
            return "***"
        return f"{value[:2]}***{value[-2:]}"

    def _summary(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary: Dict[str, Any] = {"real_candidate": 0, "example_value": 0, "secret_candidate": 0, "config_candidate": 0, "providers": {}, "projects": {}}
        for item in items:
            summary[item["classification"]] += 1
            summary[item["sensitivity"]] += 1
            summary["providers"][item["provider_guess"]] = summary["providers"].get(item["provider_guess"], 0) + 1
            summary["projects"][item["project_guess"]] = summary["projects"].get(item["project_guess"], 0) + 1
        return summary

    def _store_report(self, report: Dict[str, Any]) -> None:
        safe_report = dict(report)

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("env_intake_reports", [])
            state["env_intake_reports"].append(safe_report)
            state["env_intake_reports"] = state["env_intake_reports"][-100:]
            return state

        VAULT_CONTRACT_STORE.update(mutate)

    def _store_secret_refs_from_report(self, report: Dict[str, Any]) -> None:
        refs = []
        for item in report.get("items", []):
            refs.append({k: item[k] for k in ("secret_ref_id", "key", "classification", "sensitivity", "provider_guess", "project_guess", "environment_name", "value_fingerprint", "value_length", "requires_local_vault_value")})

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            existing = {item.get("secret_ref_id"): item for item in state.get("secret_refs", [])}
            for ref in refs:
                existing[ref["secret_ref_id"]] = {**ref, "updated_at": self._now()}
            state["secret_refs"] = list(existing.values())[-500:]
            return state

        VAULT_CONTRACT_STORE.update(mutate)

    def _store_placement_plan(self, plan: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("placement_plans", [])
            state["placement_plans"].append(plan)
            state["placement_plans"] = state["placement_plans"][-100:]
            return state

        VAULT_CONTRACT_STORE.update(mutate)


local_encrypted_vault_contract_service = LocalEncryptedVaultContractService()
