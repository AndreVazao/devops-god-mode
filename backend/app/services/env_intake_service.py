from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class EnvIntakeService:
    def __init__(self, store_path: str = "data/env_intake_store.json") -> None:
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text(json.dumps({"imports": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_store(self) -> Dict[str, Any]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, payload: Dict[str, Any]) -> None:
        self.store_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _infer_provider(self, key: str) -> str:
        upper = key.upper()
        if upper.startswith("STRIPE_"):
            return "stripe"
        if upper.startswith("PAYPAL_"):
            return "paypal"
        if upper.startswith("OPENAI_"):
            return "openai"
        if upper.startswith("DATABASE_") or upper.endswith("DATABASE_URL"):
            return "database"
        if upper.startswith("NEXT_PUBLIC_"):
            return "frontend_public"
        if upper.startswith("SUPABASE_"):
            return "supabase"
        if upper.startswith("VERCEL_"):
            return "vercel"
        if upper.startswith("GITHUB_"):
            return "github"
        return "generic"

    def _infer_scope(self, key: str) -> str:
        upper = key.upper()
        if upper.startswith("NEXT_PUBLIC_"):
            return "frontend_runtime"
        if upper.endswith("URL") or upper.endswith("URI"):
            return "service_endpoint"
        if upper.endswith("KEY") or upper.endswith("TOKEN") or upper.endswith("SECRET"):
            return "deploy_runtime"
        return "application_runtime"

    def parse_env_text(self, env_text: str, source_name: str, target_project: str, environment_name: str) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        for raw_line in env_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            provider = self._infer_provider(key)
            scope = self._infer_scope(key)
            items.append(
                {
                    "key": key,
                    "value": value,
                    "masked_value": (value[:2] + "***" + value[-2:]) if len(value) >= 6 else "***",
                    "provider": provider,
                    "usage_scope": scope,
                    "target_project": target_project,
                    "environment_name": environment_name,
                    "source_name": source_name,
                }
            )
        store = self._read_store()
        record = {
            "source_name": source_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "item_count": len(items),
            "items": items,
        }
        imports = store.get("imports", [])
        imports.append(record)
        store["imports"] = imports
        self._write_store(store)
        return {
            "ok": True,
            "mode": "env_intake_result",
            "parse_status": "env_parsed",
            "source_name": source_name,
            "target_project": target_project,
            "environment_name": environment_name,
            "item_count": len(items),
            "items": items,
        }

    def get_status(self) -> Dict[str, Any]:
        store = self._read_store()
        return {
            "ok": True,
            "mode": "env_intake_status",
            "store_path": str(self.store_path),
            "import_count": len(store.get("imports", [])),
            "status": "env_intake_ready",
        }

    def get_package(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "env_intake_package",
            "package": {
                "status": self.get_status(),
                "package_status": "env_intake_ready",
            },
        }


env_intake_service = EnvIntakeService()
