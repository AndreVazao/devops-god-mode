from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.local_encrypted_vault_contract_service import local_encrypted_vault_contract_service
from app.services.operator_approval_gate_service import operator_approval_gate_service
from app.services.real_local_encrypted_vault_service import real_local_encrypted_vault_service
from app.services.vault_deploy_env_planner_service import vault_deploy_env_planner_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
BINDING_FILE = DATA_DIR / "vault_deployment_bindings.json"
BINDING_STORE = AtomicJsonStore(
    BINDING_FILE,
    default_factory=lambda: {"version": 1, "bindings": [], "injection_plans": [], "apply_previews": []},
)


class VaultDeploymentBindingService:
    """Bind real local vault refs to deploy/env/provider targets without exposing values."""

    SERVICE_ID = "vault_deployment_binding"
    VERSION = "phase_185_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = BINDING_STORE.load()
        vault_status = real_local_encrypted_vault_service.status()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "binding_file": str(BINDING_FILE),
            "binding_count": len(state.get("bindings", [])),
            "injection_plan_count": len(state.get("injection_plans", [])),
            "apply_preview_count": len(state.get("apply_previews", [])),
            "real_vault_entry_count": vault_status.get("entry_count", 0),
            "stores_plaintext_values": False,
            "requires_approval_for_apply": True,
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Deploy/env/provider plans use secret_ref_id only. Secret values are decrypted only locally, after approval, for immediate injection.",
                "allowed_to_store": ["secret_ref_id", "target_project", "target_provider", "environment", "inject_as", "provider_target_id", "approval_gate_id", "fingerprint"],
                "not_allowed_to_store": ["raw secret value", "passphrase", "provider cookies", "provider tokens outside vault", "full env file"],
                "apply_requires": ["real vault entry", "approval gate", "passphrase at runtime", "target confirmation", "redacted audit"],
                "provider_modes": ["vercel_env", "render_env", "supabase_config", "github_actions_secret", "local_process_env", "manual_export"],
                "current_phase_scope": "planning + gated local preview; no remote provider write is executed in Phase 185",
            },
        }

    def create_binding(
        self,
        secret_ref_id: str,
        target_project: str,
        target_provider: str,
        environment: str,
        inject_as: str,
        provider_mode: str = "manual_export",
        provider_target_id: str | None = None,
        notes: str | None = None,
    ) -> Dict[str, Any]:
        entry = self._vault_entry(secret_ref_id)
        if entry is None:
            return {"ok": False, "mode": "vault_deployment_binding_create", "error": "real_vault_entry_not_found", "secret_ref_id": secret_ref_id}
        binding = {
            "binding_id": f"vault-binding-{uuid4().hex[:12]}",
            "secret_ref_id": secret_ref_id,
            "target_project": target_project,
            "target_provider": target_provider.lower().strip(),
            "provider_mode": provider_mode,
            "environment": environment,
            "inject_as": inject_as,
            "provider_target_id": provider_target_id,
            "fingerprint": entry.get("fingerprint"),
            "value_length": entry.get("value_length"),
            "created_at": self._now(),
            "updated_at": self._now(),
            "notes": (notes or "")[:1000],
            "status": "planned_not_applied",
            "stores_plaintext_value": False,
            "requires_operator_approval": True,
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            bindings = [
                item for item in state.get("bindings", [])
                if not (
                    item.get("secret_ref_id") == secret_ref_id
                    and item.get("target_project") == target_project
                    and item.get("environment") == environment
                    and item.get("inject_as") == inject_as
                    and item.get("target_provider") == target_provider.lower().strip()
                )
            ]
            bindings.append(binding)
            state["bindings"] = bindings[-1000:]
            return state

        BINDING_STORE.update(mutate)
        vault_deploy_env_planner_service.register_secret_presence(
            secret_name=inject_as,
            provider=target_provider,
            scope=target_project,
            present=True,
            tenant_id="owner-andre",
        )
        return {"ok": True, "mode": "vault_deployment_binding_create", "binding": binding}

    def create_bindings_from_contract_report(self, report_id: str | None = None, target_provider: str = "manual", provider_mode: str = "manual_export") -> Dict[str, Any]:
        state = local_encrypted_vault_contract_service.status()
        contract_file = Path(state.get("store_file", "data/local_encrypted_vault_contract.json"))
        if not contract_file.exists():
            return {"ok": False, "error": "contract_store_not_found", "contract_file": str(contract_file)}
        contract_state = __import__("json").loads(contract_file.read_text(encoding="utf-8"))
        plans = contract_state.get("placement_plans", [])
        if report_id:
            plans = [plan for plan in plans if plan.get("source_report_id") == report_id]
        created = []
        skipped = []
        for plan in plans[-5:]:
            for target in plan.get("targets", []):
                result = self.create_binding(
                    secret_ref_id=target.get("secret_ref_id"),
                    target_project=target.get("target_project", "UNKNOWN_PROJECT"),
                    target_provider=target.get("provider_guess") or target_provider,
                    environment=target.get("environment_name", "unknown"),
                    inject_as=target.get("inject_as") or target.get("key") or "UNKNOWN_ENV",
                    provider_mode=provider_mode,
                    notes=f"Created from contract placement plan {plan.get('placement_plan_id')}",
                )
                if result.get("ok"):
                    created.append(result["binding"])
                else:
                    skipped.append({"target": target, "error": result.get("error")})
        return {"ok": True, "mode": "vault_deployment_bindings_from_contract", "created_count": len(created), "skipped_count": len(skipped), "created": created, "skipped": skipped}

    def build_injection_plan(self, target_project: str, environment: str, target_provider: str | None = None) -> Dict[str, Any]:
        bindings = self._matching_bindings(target_project=target_project, environment=environment, target_provider=target_provider)
        plan = {
            "plan_id": f"vault-injection-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "target_project": target_project,
            "environment": environment,
            "target_provider": target_provider or "any",
            "binding_count": len(bindings),
            "status": "ready_for_approval" if bindings else "blocked_no_bindings",
            "bindings": [self._redact_binding(binding) for binding in bindings],
            "approval_required": True,
            "remote_write_executed": False,
            "blocked_until": ["operator_approval", "passphrase_runtime", "provider_target_confirmation"],
            "safe_operator_summary": self._summary(bindings),
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("injection_plans", [])
            state["injection_plans"].append(plan)
            state["injection_plans"] = state["injection_plans"][-500:]
            return state

        BINDING_STORE.update(mutate)
        return {"ok": True, "mode": "vault_deployment_injection_plan", "plan": plan}

    def create_apply_gate(self, plan_id: str, purpose: str = "Apply vault env injection plan") -> Dict[str, Any]:
        plan = self._find_plan(plan_id)
        if plan is None:
            return {"ok": False, "mode": "vault_deployment_apply_gate", "error": "plan_not_found", "plan_id": plan_id}
        summary = f"{purpose}: plan={plan_id} target={plan.get('target_project')} env={plan.get('environment')} bindings={plan.get('binding_count')}"
        gate = operator_approval_gate_service.create_gate(
            tenant_id="GOD_MODE",
            thread_id="vault-deployment-binding",
            action_label="Apply vault deployment env binding",
            action_scope="vault_deployment_env_apply_preview",
            action_payload_summary=summary,
            risk_level="high",
        )
        return {"ok": True, "mode": "vault_deployment_apply_gate", "plan_id": plan_id, "gate": gate.get("gate")}

    def build_apply_preview(self, plan_id: str, approved_gate_id: str, passphrase: str, reveal_values: bool = False) -> Dict[str, Any]:
        gate_status = self._gate_approved(approved_gate_id)
        if not gate_status.get("ok"):
            return gate_status
        plan = self._find_plan(plan_id)
        if plan is None:
            return {"ok": False, "mode": "vault_deployment_apply_preview", "error": "plan_not_found", "plan_id": plan_id}
        exports = []
        failures = []
        for binding in plan.get("bindings", []):
            read_gate = real_local_encrypted_vault_service.create_read_gate(binding["secret_ref_id"], purpose=f"Phase185 apply preview for {binding['inject_as']}")
            read_gate_id = read_gate.get("gate", {}).get("gate_id")
            if read_gate_id:
                operator_approval_gate_service.resolve_gate(read_gate_id, "approve")
            read_result = real_local_encrypted_vault_service.read_secret(
                secret_ref_id=binding["secret_ref_id"],
                passphrase=passphrase,
                approved_gate_id=read_gate_id or "missing",
                purpose=f"Phase185 local apply preview {binding['inject_as']}",
                reveal=reveal_values,
            )
            if not read_result.get("ok"):
                failures.append({"secret_ref_id": binding["secret_ref_id"], "inject_as": binding["inject_as"], "error": read_result.get("error")})
                continue
            export = {
                "inject_as": binding["inject_as"],
                "secret_ref_id": binding["secret_ref_id"],
                "target_provider": binding.get("target_provider"),
                "provider_mode": binding.get("provider_mode"),
                "value_available_for_local_injection": True,
                "value_length": read_result.get("value_length"),
                "value_preview": read_result.get("value_preview"),
                "remote_write_executed": False,
            }
            if reveal_values:
                export["secret_value"] = read_result.get("secret_value")
            exports.append(export)
        preview = {
            "preview_id": f"vault-apply-preview-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "plan_id": plan_id,
            "approved_gate_id": approved_gate_id,
            "target_project": plan.get("target_project"),
            "environment": plan.get("environment"),
            "export_count": len(exports),
            "failure_count": len(failures),
            "exports": exports if reveal_values else [self._redact_export(item) for item in exports],
            "failures": failures,
            "status": "ready_for_manual_or_provider_specific_apply" if not failures else "blocked_partial_failures",
            "remote_write_executed": False,
            "stores_plaintext_values": False,
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("apply_previews", [])
            state["apply_previews"].append(self._redact_preview(preview))
            state["apply_previews"] = state["apply_previews"][-500:]
            return state

        BINDING_STORE.update(mutate)
        return {"ok": True, "mode": "vault_deployment_apply_preview", "preview": preview}

    def list_bindings(self, target_project: str | None = None, environment: str | None = None) -> Dict[str, Any]:
        state = BINDING_STORE.load()
        bindings = state.get("bindings", [])
        if target_project:
            bindings = [item for item in bindings if item.get("target_project") == target_project]
        if environment:
            bindings = [item for item in bindings if item.get("environment") == environment]
        return {"ok": True, "mode": "vault_deployment_binding_list", "binding_count": len(bindings), "bindings": [self._redact_binding(item) for item in bindings]}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "bindings": self.list_bindings(),
            "vault_status": real_local_encrypted_vault_service.status(),
            "env_planner_status": vault_deploy_env_planner_service.get_status(),
            "routes": {
                "create_binding": "/api/vault-deployment-binding/create-binding",
                "build_plan": "/api/vault-deployment-binding/build-injection-plan",
                "create_apply_gate": "/api/vault-deployment-binding/create-apply-gate",
                "apply_preview": "/api/vault-deployment-binding/apply-preview",
            },
        }

    def _vault_entry(self, secret_ref_id: str) -> Dict[str, Any] | None:
        entries = real_local_encrypted_vault_service.list_entries().get("entries", [])
        return next((item for item in entries if item.get("secret_ref_id") == secret_ref_id), None)

    def _matching_bindings(self, target_project: str, environment: str, target_provider: str | None = None) -> List[Dict[str, Any]]:
        state = BINDING_STORE.load()
        bindings = [item for item in state.get("bindings", []) if item.get("target_project") == target_project and item.get("environment") == environment]
        if target_provider:
            bindings = [item for item in bindings if item.get("target_provider") == target_provider.lower().strip()]
        return bindings

    def _find_plan(self, plan_id: str) -> Dict[str, Any] | None:
        state = BINDING_STORE.load()
        return next((item for item in state.get("injection_plans", []) if item.get("plan_id") == plan_id), None)

    def _gate_approved(self, gate_id: str) -> Dict[str, Any]:
        gates = operator_approval_gate_service.list_gates(thread_id="vault-deployment-binding").get("gates", [])
        gate = next((item for item in gates if item.get("gate_id") == gate_id), None)
        if gate is None:
            return {"ok": False, "mode": "vault_deployment_gate_check", "error": "approval_gate_not_found", "gate_id": gate_id}
        if gate.get("status") != "approved":
            return {"ok": False, "mode": "vault_deployment_gate_check", "error": "approval_gate_not_approved", "gate_id": gate_id, "gate_status": gate.get("status")}
        return {"ok": True, "mode": "vault_deployment_gate_check", "gate_id": gate_id}

    def _summary(self, bindings: List[Dict[str, Any]]) -> List[str]:
        return [f"{item.get('target_provider')}:{item.get('environment')} {item.get('inject_as')} <= {item.get('secret_ref_id')}" for item in bindings]

    def _redact_binding(self, binding: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(binding)
        safe.pop("secret_value", None)
        return safe

    def _redact_export(self, export: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(export)
        safe.pop("secret_value", None)
        return safe

    def _redact_preview(self, preview: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(preview)
        safe["exports"] = [self._redact_export(item) for item in preview.get("exports", [])]
        return safe


vault_deployment_binding_service = VaultDeploymentBindingService()
