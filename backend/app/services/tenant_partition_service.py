from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class TenantPartitionService:
    def __init__(self, store_path: str = "data/tenant_partition_store.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"tenants": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "tenant_partition_status",
            "store_path": str(self.store_path),
            "tenant_count": len(store.get("tenants", [])),
            "status": "tenant_partition_ready",
        }

    def upsert_tenant(
        self,
        tenant_id: str,
        owner_type: str,
        display_name: str,
        repo_scope_mode: str,
        provider_scope_mode: str,
        vault_namespace: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        store = self._read_store()
        tenants = [item for item in store.get("tenants", []) if item.get("tenant_id") != tenant_id]
        tenant = {
            "tenant_id": tenant_id,
            "owner_type": owner_type,
            "display_name": display_name,
            "repo_scope_mode": repo_scope_mode,
            "provider_scope_mode": provider_scope_mode,
            "vault_namespace": vault_namespace,
            "notes": notes,
        }
        tenants.append(tenant)
        store["tenants"] = tenants
        self._write_store(store)
        return {
            "ok": True,
            "mode": "tenant_partition_upsert_result",
            "upsert_status": "tenant_partition_saved",
            "tenant": tenant,
        }

    def list_tenants(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "tenant_partition_list_result",
            "tenant_count": len(store.get("tenants", [])),
            "tenants": store.get("tenants", []),
        }

    def build_partition_plan(self, tenant_id: str, project_name: str, multirepo_mode: bool = False) -> Dict[str, Any]:
        store = self._read_store()
        tenant = next((item for item in store.get("tenants", []) if item.get("tenant_id") == tenant_id), None)
        if tenant is None:
            return {
                "ok": False,
                "mode": "tenant_partition_plan_result",
                "plan_status": "tenant_not_found",
                "tenant_id": tenant_id,
            }
        plan = {
            "tenant_id": tenant_id,
            "display_name": tenant.get("display_name"),
            "repo_scope_mode": tenant.get("repo_scope_mode"),
            "provider_scope_mode": tenant.get("provider_scope_mode"),
            "vault_namespace": tenant.get("vault_namespace"),
            "project_name": project_name,
            "multirepo_mode": multirepo_mode,
            "frontend_repo": f"{project_name}-frontend" if multirepo_mode else project_name,
            "backend_repo": f"{project_name}-backend" if multirepo_mode else project_name,
            "visibility_rules": [
                "Only show repos linked to this tenant by default.",
                "Only show provider sessions linked to this tenant by default.",
                "Vault reads must be namespaced by tenant.",
                "Cross-tenant access requires explicit operator action.",
            ],
        }
        return {
            "ok": True,
            "mode": "tenant_partition_plan_result",
            "plan_status": "tenant_partition_plan_ready",
            "plan": plan,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "tenant_partition_package",
            "package": {
                "status": self.get_status(),
                "package_status": "tenant_partition_ready",
            },
        }


tenant_partition_service = TenantPartitionService()
