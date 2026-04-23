from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.secret_vault_service import secret_vault_service


class DeploymentSecretBindingService:
    def __init__(self, binding_path: str = "data/deployment_secret_bindings.json") -> None:
        self.binding_path = Path(binding_path)
        self.binding_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.binding_path.exists():
            self.binding_path.write_text(json.dumps({"bindings": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.binding_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.binding_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "deployment_secret_binding_status",
            "binding_path": str(self.binding_path),
            "binding_count": len(store.get("bindings", [])),
            "status": "deployment_secret_binding_ready",
        }

    def bind_secret(
        self,
        target_name: str,
        environment_name: str,
        secret_name: str,
        inject_as: str,
    ) -> Dict[str, Any]:
        secrets = secret_vault_service.list_secrets().get("secrets", [])
        secret_record = next((item for item in secrets if item.get("secret_name") == secret_name), None)
        if not secret_record:
            return {
                "ok": False,
                "mode": "deployment_secret_binding_result",
                "binding_status": "secret_not_found",
                "secret_name": secret_name,
            }

        store = self._read_store()
        bindings = [
            item for item in store.get("bindings", [])
            if not (item.get("target_name") == target_name and item.get("environment_name") == environment_name and item.get("inject_as") == inject_as)
        ]
        binding = {
            "target_name": target_name,
            "environment_name": environment_name,
            "secret_name": secret_name,
            "inject_as": inject_as,
            "provider": secret_record.get("provider"),
            "usage_scope": secret_record.get("usage_scope"),
            "fingerprint": secret_record.get("fingerprint"),
        }
        bindings.append(binding)
        store["bindings"] = bindings
        self._write_store(store)
        return {
            "ok": True,
            "mode": "deployment_secret_binding_result",
            "binding_status": "secret_bound",
            "binding": binding,
        }

    def build_deploy_secret_plan(self, target_name: str, environment_name: str) -> Dict[str, Any]:
        store = self._read_store()
        bindings = [
            item for item in store.get("bindings", [])
            if item.get("target_name") == target_name and item.get("environment_name") == environment_name
        ]
        return {
            "ok": True,
            "mode": "deployment_secret_binding_plan",
            "target_name": target_name,
            "environment_name": environment_name,
            "binding_count": len(bindings),
            "bindings": bindings,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "deployment_secret_binding_package",
            "package": {
                "status": self.get_status(),
                "package_status": "deployment_secret_binding_ready",
            },
        }


deployment_secret_binding_service = DeploymentSecretBindingService()
