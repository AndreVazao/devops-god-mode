from __future__ import annotations

from typing import Any, Dict, List

from app.services.deployment_secret_binding_service import deployment_secret_binding_service
from app.services.env_intake_service import env_intake_service
from app.services.secret_vault_service import secret_vault_service


class EnvVaultImportService:
    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "env_vault_import_status",
            "status": "env_vault_import_ready",
        }

    def import_env_text(self, env_text: str, source_name: str, target_project: str, environment_name: str) -> Dict[str, Any]:
        parsed = env_intake_service.parse_env_text(
            env_text=env_text,
            source_name=source_name,
            target_project=target_project,
            environment_name=environment_name,
        )
        imported: List[Dict[str, Any]] = []
        for item in parsed.get("items", []):
            register_result = secret_vault_service.register_secret(
                secret_name=item["key"],
                secret_value=item["value"],
                provider=item["provider"],
                usage_scope=item["usage_scope"],
                target_refs=[f"{target_project}:{environment_name}", source_name],
            )
            binding_result = deployment_secret_binding_service.bind_secret(
                target_name=target_project,
                environment_name=environment_name,
                secret_name=item["key"],
                inject_as=item["key"],
            )
            imported.append(
                {
                    "key": item["key"],
                    "provider": item["provider"],
                    "usage_scope": item["usage_scope"],
                    "register_status": register_result.get("register_status"),
                    "binding_status": binding_result.get("binding_status"),
                }
            )
        return {
            "ok": True,
            "mode": "env_vault_import_result",
            "import_status": "env_imported_to_vault",
            "source_name": source_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "imported_count": len(imported),
            "imported": imported,
            "parsed_item_count": parsed.get("item_count", 0),
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "env_vault_import_package",
            "package": {
                "status": self.get_status(),
                "package_status": "env_vault_import_ready",
            },
        }


env_vault_import_service = EnvVaultImportService()
