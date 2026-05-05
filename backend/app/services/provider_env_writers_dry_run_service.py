from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.operator_approval_gate_service import operator_approval_gate_service
from app.services.vault_deployment_binding_service import vault_deployment_binding_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
DRY_RUN_FILE = DATA_DIR / "provider_env_writers_dry_run.json"
DRY_RUN_STORE = AtomicJsonStore(
    DRY_RUN_FILE,
    default_factory=lambda: {"version": 1, "dry_runs": [], "writer_specs": [], "promotion_gates": []},
)


class ProviderEnvWritersDryRunService:
    """Provider-specific env writer payloads in dry-run mode only.

    Phase 186 intentionally does not execute remote provider writes. It converts
    a vault deployment apply preview into provider-specific redacted payloads and
    requires approval before building the dry-run.
    """

    SERVICE_ID = "provider_env_writers_dry_run"
    VERSION = "phase_186_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = DRY_RUN_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "dry_run_file": str(DRY_RUN_FILE),
            "dry_run_count": len(state.get("dry_runs", [])),
            "writer_spec_count": len(state.get("writer_specs", [])),
            "remote_write_enabled": False,
            "requires_approval_for_dry_run": True,
            "stores_plaintext_values": False,
            "supported_providers": ["vercel", "render", "supabase", "github_actions", "local_process", "manual"],
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "phase_scope": "provider-specific payload generation in dry-run only",
                "remote_write_enabled": False,
                "no_network_calls": True,
                "allowed_inputs": ["vault_deployment_apply_preview", "secret_ref_id", "inject_as", "target_provider", "provider_mode"],
                "stored_outputs": ["redacted provider payload", "payload_hash", "target metadata", "approval gate id"],
                "blocked": ["provider API write", "raw secret value in store", "passphrase persistence", "GitHub secret write", "Vercel/Render/Supabase mutation"],
                "promotion_to_real_write_requires_future_phase": True,
            },
        }

    def create_dry_run_gate(self, plan_id: str, provider: str, purpose: str = "Build provider env dry-run payload") -> Dict[str, Any]:
        summary = f"{purpose}: plan={plan_id} provider={provider} dry-run only; no remote write"
        gate = operator_approval_gate_service.create_gate(
            tenant_id="GOD_MODE",
            thread_id="provider-env-writers-dry-run",
            action_label="Build provider env writer dry-run",
            action_scope="provider_env_writer_dry_run",
            action_payload_summary=summary,
            risk_level="medium",
        )
        return {"ok": True, "mode": "provider_env_dry_run_gate", "gate": gate.get("gate"), "remote_write_enabled": False}

    def build_from_injection_plan(
        self,
        plan_id: str,
        approved_gate_id: str,
        passphrase: str,
        provider: str | None = None,
    ) -> Dict[str, Any]:
        gate_status = self._gate_approved(approved_gate_id)
        if not gate_status.get("ok"):
            return gate_status
        apply_gate = vault_deployment_binding_service.create_apply_gate(plan_id, purpose="Phase186 provider env writer dry-run source preview")
        if not apply_gate.get("ok"):
            return apply_gate
        apply_gate_id = apply_gate.get("gate", {}).get("gate_id")
        if apply_gate_id:
            operator_approval_gate_service.resolve_gate(apply_gate_id, "approve")
        preview = vault_deployment_binding_service.build_apply_preview(
            plan_id=plan_id,
            approved_gate_id=apply_gate_id or "missing",
            passphrase=passphrase,
            reveal_values=True,
        )
        if not preview.get("ok"):
            return preview
        return self.build_from_apply_preview(preview["preview"], approved_gate_id=approved_gate_id, provider=provider)

    def build_from_apply_preview(self, preview: Dict[str, Any], approved_gate_id: str, provider: str | None = None) -> Dict[str, Any]:
        gate_status = self._gate_approved(approved_gate_id)
        if not gate_status.get("ok"):
            return gate_status
        provider_filter = provider.lower().strip() if provider else None
        exports = preview.get("exports", [])
        payloads = []
        failures = []
        for export in exports:
            target_provider = (provider_filter or export.get("target_provider") or "manual").lower().strip()
            try:
                payloads.append(self._provider_payload(target_provider, export, preview))
            except Exception as exc:
                failures.append({"inject_as": export.get("inject_as"), "target_provider": target_provider, "error": str(exc)})
        dry_run = {
            "dry_run_id": f"provider-dry-run-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "approved_gate_id": approved_gate_id,
            "source_plan_id": preview.get("plan_id"),
            "target_project": preview.get("target_project"),
            "environment": preview.get("environment"),
            "provider_filter": provider_filter or "from_exports",
            "payload_count": len(payloads),
            "failure_count": len(failures),
            "payloads": [self._redact_payload(payload) for payload in payloads],
            "failures": failures,
            "remote_write_executed": False,
            "remote_write_enabled": False,
            "stores_plaintext_values": False,
            "status": "dry_run_ready" if not failures else "dry_run_partial_failures",
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault("dry_runs", [])
            state["dry_runs"].append(dry_run)
            state["dry_runs"] = state["dry_runs"][-500:]
            return state

        DRY_RUN_STORE.update(mutate)
        return {"ok": True, "mode": "provider_env_writer_dry_run", "dry_run": dry_run}

    def writer_specs(self) -> Dict[str, Any]:
        specs = [
            {
                "provider": "vercel",
                "mode": "vercel_env",
                "method_future": "Vercel API project env create/update",
                "required_target_fields": ["VERCEL_PROJECT_ID or provider_target_id", "environment", "key", "value"],
                "phase_186_behavior": "dry_run_payload_only",
            },
            {
                "provider": "render",
                "mode": "render_env",
                "method_future": "Render API environment group/service env var sync",
                "required_target_fields": ["RENDER_SERVICE_ID or provider_target_id", "key", "value"],
                "phase_186_behavior": "dry_run_payload_only",
            },
            {
                "provider": "supabase",
                "mode": "supabase_config",
                "method_future": "Supabase project config/secrets edge functions when applicable",
                "required_target_fields": ["SUPABASE_PROJECT_REF or provider_target_id", "key", "value"],
                "phase_186_behavior": "dry_run_payload_only",
            },
            {
                "provider": "github_actions",
                "mode": "github_actions_secret",
                "method_future": "GitHub Actions encrypted secrets API",
                "required_target_fields": ["repository_full_name", "public_key", "encrypted_value"],
                "phase_186_behavior": "dry_run_payload_only_redacted_and_hash_only",
            },
            {
                "provider": "local_process",
                "mode": "local_process_env",
                "method_future": "local env injection into subprocess/service runtime",
                "required_target_fields": ["process_profile", "key", "value"],
                "phase_186_behavior": "dry_run_payload_only",
            },
        ]
        return {"ok": True, "mode": "provider_env_writer_specs", "spec_count": len(specs), "specs": specs}

    def list_dry_runs(self, limit: int = 50) -> Dict[str, Any]:
        state = DRY_RUN_STORE.load()
        runs = list(reversed(state.get("dry_runs", [])))[0:max(1, min(limit, 200))]
        return {"ok": True, "mode": "provider_env_writer_dry_run_list", "dry_run_count": len(runs), "dry_runs": runs}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "writer_specs": self.writer_specs(),
            "recent_dry_runs": self.list_dry_runs(limit=20),
            "routes": {
                "create_gate": "/api/provider-env-writers-dry-run/create-gate",
                "build_from_plan": "/api/provider-env-writers-dry-run/build-from-plan",
                "build_from_preview": "/api/provider-env-writers-dry-run/build-from-preview",
            },
        }

    def _provider_payload(self, provider: str, export: Dict[str, Any], preview: Dict[str, Any]) -> Dict[str, Any]:
        value = export.get("secret_value")
        if value is None:
            raise ValueError("secret_value_required_for_dry_run_payload_build")
        key = export.get("inject_as") or "UNKNOWN_ENV"
        value_hash = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
        base = {
            "provider": provider,
            "provider_mode": export.get("provider_mode") or self._default_mode(provider),
            "target_project": preview.get("target_project"),
            "environment": preview.get("environment"),
            "secret_ref_id": export.get("secret_ref_id"),
            "key": key,
            "value_length": len(str(value)),
            "value_hash": value_hash,
            "value_preview": self._preview(str(value)),
            "remote_write_executed": False,
        }
        if provider == "vercel":
            base["dry_run_request"] = {"method": "POST", "path": "/v10/projects/{projectId}/env", "json": {"key": key, "target": [preview.get("environment")], "type": "encrypted", "value": "***REDACTED***"}}
        elif provider == "render":
            base["dry_run_request"] = {"method": "PATCH", "path": "/v1/services/{serviceId}/env-vars", "json": [{"key": key, "value": "***REDACTED***"}]}
        elif provider == "supabase":
            base["dry_run_request"] = {"method": "CONFIG", "path": "supabase project/edge-function secret", "json": {"name": key, "value": "***REDACTED***"}}
        elif provider in {"github_actions", "github"}:
            encrypted_placeholder = base64.urlsafe_b64encode(hashlib.sha256(str(value).encode()).digest()).decode("ascii")
            base["provider"] = "github_actions"
            base["dry_run_request"] = {"method": "PUT", "path": "/repos/{owner}/{repo}/actions/secrets/{secret_name}", "json": {"encrypted_value": encrypted_placeholder, "key_id": "DRY_RUN_PUBLIC_KEY_ID"}}
        elif provider == "local_process":
            base["dry_run_request"] = {"method": "LOCAL_ENV", "path": "process environment", "env": {key: "***REDACTED***"}}
        else:
            base["dry_run_request"] = {"method": "MANUAL", "path": "manual export", "env": {key: "***REDACTED***"}}
        return base

    def _default_mode(self, provider: str) -> str:
        return {
            "vercel": "vercel_env",
            "render": "render_env",
            "supabase": "supabase_config",
            "github": "github_actions_secret",
            "github_actions": "github_actions_secret",
            "local_process": "local_process_env",
        }.get(provider, "manual_export")

    def _redact_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(payload)
        safe.pop("secret_value", None)
        return safe

    def _preview(self, value: str) -> str:
        if len(value) <= 6:
            return "***"
        return f"{value[:2]}***{value[-2:]}"

    def _gate_approved(self, gate_id: str) -> Dict[str, Any]:
        gates = operator_approval_gate_service.list_gates(thread_id="provider-env-writers-dry-run").get("gates", [])
        gate = next((item for item in gates if item.get("gate_id") == gate_id), None)
        if gate is None:
            return {"ok": False, "mode": "provider_env_writer_gate_check", "error": "approval_gate_not_found", "gate_id": gate_id}
        if gate.get("status") != "approved":
            return {"ok": False, "mode": "provider_env_writer_gate_check", "error": "approval_gate_not_approved", "gate_id": gate_id, "gate_status": gate.get("status")}
        return {"ok": True, "mode": "provider_env_writer_gate_check", "gate_id": gate_id}


provider_env_writers_dry_run_service = ProviderEnvWritersDryRunService()
