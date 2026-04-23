from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from app.services.tenant_partition_service import tenant_partition_service


class TenantMultirepoLinkageService:
    def __init__(self, linkage_root: str = "data/tenant_multirepo_linkage") -> None:
        self.linkage_root = Path(linkage_root)
        self.linkage_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> Dict[str, Any]:
        manifest_count = len([p for p in self.linkage_root.rglob("*.json")]) if self.linkage_root.exists() else 0
        return {
            "ok": True,
            "mode": "tenant_multirepo_linkage_status",
            "linkage_root": str(self.linkage_root),
            "manifest_count": manifest_count,
            "status": "tenant_multirepo_linkage_ready",
        }

    def build_linkage(
        self,
        tenant_id: str,
        project_name: str,
        frontend_runtime: str,
        backend_runtime: str,
    ) -> Dict[str, Any]:
        partition = tenant_partition_service.build_partition_plan(
            tenant_id=tenant_id,
            project_name=project_name,
            multirepo_mode=True,
        )
        if not partition.get("ok"):
            return {
                "ok": False,
                "mode": "tenant_multirepo_linkage_result",
                "linkage_status": "tenant_not_found",
                "tenant_id": tenant_id,
                "project_name": project_name,
            }
        plan = partition["plan"]
        linkage = {
            "tenant_id": tenant_id,
            "project_name": project_name,
            "frontend_repo": plan["frontend_repo"],
            "backend_repo": plan["backend_repo"],
            "frontend_runtime": frontend_runtime,
            "backend_runtime": backend_runtime,
            "shared_contracts": [
                "frontend uses public api base url from tenant scoped env projection",
                "backend uses tenant scoped secret bindings and database credentials",
                "cross repo delivery requires explicit tenant context",
            ],
        }
        manifest_path = self.linkage_root / tenant_id / project_name / "tenant-multirepo-linkage.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(linkage, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "mode": "tenant_multirepo_linkage_result",
            "linkage_status": "tenant_multirepo_linkage_ready",
            "tenant_id": tenant_id,
            "project_name": project_name,
            "frontend_repo": linkage["frontend_repo"],
            "backend_repo": linkage["backend_repo"],
            "manifest_file": str(manifest_path),
            "linkage": linkage,
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "tenant_multirepo_linkage_package",
            "package": {
                "status": self.get_status(),
                "package_status": "tenant_multirepo_linkage_ready",
            },
        }


tenant_multirepo_linkage_service = TenantMultirepoLinkageService()
