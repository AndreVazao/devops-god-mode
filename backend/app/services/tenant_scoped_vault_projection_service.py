from __future__ import annotations

from typing import Any, Dict, List

from app.services.secret_vault_service import secret_vault_service
from app.services.tenant_partition_service import tenant_partition_service


class TenantScopedVaultProjectionService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "tenant_scoped_vault_projection_status",
            "status": "tenant_scoped_vault_projection_ready",
        }

    def build_projection(self, tenant_id: str) -> Dict[str, Any]:
        tenant_plan = tenant_partition_service.build_partition_plan(
            tenant_id=tenant_id,
            project_name="tenant-scope-projection",
            multirepo_mode=False,
        )
        if not tenant_plan.get("ok"):
            return {
                "ok": False,
                "mode": "tenant_scoped_vault_projection_result",
                "projection_status": "tenant_not_found",
                "tenant_id": tenant_id,
            }
        namespace = tenant_plan["plan"]["vault_namespace"]
        secrets = secret_vault_service.list_secrets().get("secrets", [])
        visible: List[Dict[str, Any]] = []
        for item in secrets:
            refs = item.get("target_refs", [])
            if any(namespace in ref or tenant_id in ref for ref in refs):
                visible.append(
                    {
                        "secret_name": item.get("secret_name"),
                        "provider": item.get("provider"),
                        "usage_scope": item.get("usage_scope"),
                        "target_refs": refs,
                    }
                )
        return {
            "ok": True,
            "mode": "tenant_scoped_vault_projection_result",
            "projection_status": "tenant_scoped_projection_ready",
            "tenant_id": tenant_id,
            "vault_namespace": namespace,
            "visible_secret_count": len(visible),
            "visible_secrets": visible,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "tenant_scoped_vault_projection_package",
            "package": {
                "status": self.get_status(),
                "package_status": "tenant_scoped_vault_projection_ready",
            },
        }


tenant_scoped_vault_projection_service = TenantScopedVaultProjectionService()
