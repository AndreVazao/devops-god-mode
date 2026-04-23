from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ProviderSessionPartitionService:
    def __init__(self, store_path: str = "data/provider_session_partition_store.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"sessions": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "provider_session_partition_status",
            "store_path": str(self.store_path),
            "session_count": len(store.get("sessions", [])),
            "status": "provider_session_partition_ready",
        }

    def upsert_session(
        self,
        tenant_id: str,
        provider_name: str,
        account_label: str,
        session_scope: str,
        access_mode: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        store = self._read_store()
        key = f"{tenant_id}:{provider_name}:{account_label}"
        sessions = [item for item in store.get("sessions", []) if item.get("session_key") != key]
        session = {
            "session_key": key,
            "tenant_id": tenant_id,
            "provider_name": provider_name,
            "account_label": account_label,
            "session_scope": session_scope,
            "access_mode": access_mode,
            "notes": notes,
        }
        sessions.append(session)
        store["sessions"] = sessions
        self._write_store(store)
        return {
            "ok": True,
            "mode": "provider_session_partition_upsert_result",
            "upsert_status": "provider_session_saved",
            "session": session,
        }

    def list_sessions(self, tenant_id: str | None = None) -> Dict[str, Any]:
        store = self._read_store()
        sessions = store.get("sessions", [])
        if tenant_id:
            sessions = [item for item in sessions if item.get("tenant_id") == tenant_id]
        return {
            "ok": True,
            "mode": "provider_session_partition_list_result",
            "session_count": len(sessions),
            "sessions": sessions,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "provider_session_partition_package",
            "package": {
                "status": self.get_status(),
                "package_status": "provider_session_partition_ready",
            },
        }


provider_session_partition_service = ProviderSessionPartitionService()
