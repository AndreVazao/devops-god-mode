from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


class SecretVaultService:
    def __init__(self, vault_path: str = "data/secret_vault_store.json") -> None:
        self.vault_path = Path(vault_path)
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.vault_path.exists():
            self.vault_path.write_text(json.dumps({"secrets": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.vault_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.vault_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _fingerprint(self, secret_value: str) -> str:
        return hashlib.sha256(secret_value.encode("utf-8")).hexdigest()

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "secret_vault_status",
            "vault_path": str(self.vault_path),
            "secret_count": len(store.get("secrets", [])),
            "status": "secret_vault_ready",
        }

    def register_secret(
        self,
        secret_name: str,
        secret_value: str,
        provider: str,
        usage_scope: str,
        target_refs: List[str] | None = None,
    ) -> Dict[str, Any]:
        store = self._read_store()
        secrets = [item for item in store.get("secrets", []) if item.get("secret_name") != secret_name]
        record = {
            "secret_name": secret_name,
            "provider": provider,
            "usage_scope": usage_scope,
            "target_refs": target_refs or [],
            "fingerprint": self._fingerprint(secret_value),
            "value_length": len(secret_value),
            "has_value": bool(secret_value),
        }
        secrets.append(record)
        store["secrets"] = secrets
        self._write_store(store)
        return {
            "ok": True,
            "mode": "secret_vault_register_result",
            "register_status": "secret_registered",
            "secret": record,
        }

    def list_secrets(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "secret_vault_list_result",
            "secrets": store.get("secrets", []),
            "secret_count": len(store.get("secrets", [])),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "secret_vault_package",
            "package": {
                "status": self.get_status(),
                "package_status": "secret_vault_ready",
            },
        }


secret_vault_service = SecretVaultService()
