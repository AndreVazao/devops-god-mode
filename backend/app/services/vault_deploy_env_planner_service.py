from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.repo_relationship_graph_service import repo_relationship_graph_service

DATA_DIR = Path("data")
DEPLOY_ENV_FILE = DATA_DIR / "vault_deploy_env_planner.json"

PROVIDER_ENV_RULES = {
    "vercel": ["VERCEL_TOKEN", "VERCEL_ORG_ID", "VERCEL_PROJECT_ID"],
    "render": ["RENDER_API_KEY", "RENDER_SERVICE_ID"],
    "supabase": ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"],
    "github-actions": ["GITHUB_TOKEN"],
    "openai": ["OPENAI_API_KEY"],
}

ROLE_ENV_RULES = {
    "website": ["NEXT_PUBLIC_SITE_URL"],
    "frontend": ["NEXT_PUBLIC_API_URL"],
    "backend": ["DATABASE_URL", "CORS_ORIGINS"],
    "studio": ["ADMIN_BASE_URL"],
    "vault": ["SECRET_VAULT_NAMESPACE"],
}


class VaultDeployEnvPlannerService:
    """Vault-aware deployment and environment planner.

    This phase maps repo graph deploy targets and roles to required environment
    variables and vault secrets. It does not reveal secret values and does not
    deploy. It builds the safe readiness layer needed before real build/deploy
    execution or approval-gated PR changes.
    """

    def get_status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": "vault_deploy_env_planner_status",
            "status": "vault_deploy_env_planner_ready",
            "planner_file": str(DEPLOY_ENV_FILE),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_store(self) -> Dict[str, Any]:
        if not DEPLOY_ENV_FILE.exists():
            return {"project_env_manifests": {}, "secret_presence": {}, "readiness_reports": []}
        try:
            loaded = json.loads(DEPLOY_ENV_FILE.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return {"project_env_manifests": {}, "secret_presence": {}, "readiness_reports": []}
            loaded.setdefault("project_env_manifests", {})
            loaded.setdefault("secret_presence", {})
            loaded.setdefault("readiness_reports", [])
            return loaded
        except json.JSONDecodeError:
            return {"project_env_manifests": {}, "secret_presence": {}, "readiness_reports": []}

    def _save_store(self, store: Dict[str, Any]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DEPLOY_ENV_FILE.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return normalized or "deploy-env"

    def _required_env_for_repo(self, repo: Dict[str, Any]) -> List[str]:
        required = set()
        for target in repo.get("deploy_targets", []):
            required.update(PROVIDER_ENV_RULES.get(target, []))
        for role in repo.get("roles", []):
            required.update(ROLE_ENV_RULES.get(role, []))
        if "supabase" in repo.get("stack", []):
            required.update(PROVIDER_ENV_RULES["supabase"])
        if "github-actions" in repo.get("stack", []):
            required.update(PROVIDER_ENV_RULES["github-actions"])
        return sorted(required)

    def _classify_env(self, env_name: str) -> Dict[str, Any]:
        public_prefixes = ("NEXT_PUBLIC_", "PUBLIC_", "VITE_")
        sensitive_markers = ["TOKEN", "KEY", "SECRET", "PASSWORD", "SERVICE_ROLE", "DATABASE_URL"]
        is_public = env_name.startswith(public_prefixes)
        is_secret = (not is_public) and any(marker in env_name for marker in sensitive_markers)
        return {
            "env_name": env_name,
            "is_public": is_public,
            "is_secret": is_secret,
            "storage_target": "project_env" if is_public else "secret_vault",
        }

    def register_secret_presence(
        self,
        secret_name: str,
        provider: str = "unknown",
        scope: str = "owner-andre",
        present: bool = True,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        normalized_name = secret_name.strip().upper()
        if not normalized_name:
            return {"ok": False, "error": "secret_name_empty"}
        store = self._load_store()
        key = f"{tenant_id}:{scope}:{normalized_name}"
        record = {
            "secret_name": normalized_name,
            "provider": provider,
            "scope": scope,
            "tenant_id": tenant_id,
            "present": bool(present),
            "updated_at": self._now(),
        }
        store["secret_presence"][key] = record
        self._save_store(store)
        return {"ok": True, "mode": "vault_deploy_env_register_secret_presence", "secret": record}

    def build_project_env_manifest(
        self,
        project_id: str,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        graph = repo_relationship_graph_service.build_graph(tenant_id=tenant_id)
        project = next((item for item in graph.get("projects", []) if item.get("project_id") == project_id), None)
        if project is None:
            return {"ok": False, "error": "project_not_found", "project_id": project_id}

        repo_manifests = []
        all_required = set()
        for repo in project.get("repositories", []):
            required_env = self._required_env_for_repo(repo)
            all_required.update(required_env)
            repo_manifests.append(
                {
                    "repo_id": repo.get("repo_id"),
                    "repository_full_name": repo.get("repository_full_name"),
                    "roles": repo.get("roles", []),
                    "deploy_targets": repo.get("deploy_targets", []),
                    "stack": repo.get("stack", []),
                    "required_env": [self._classify_env(env) for env in required_env],
                }
            )

        manifest_id = f"env-{uuid4().hex[:12]}"
        manifest = {
            "manifest_id": manifest_id,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "project_name": project.get("project_name"),
            "created_at": self._now(),
            "repository_count": len(project.get("repositories", [])),
            "conversation_count": project.get("conversation_count", 0),
            "required_env_count": len(all_required),
            "required_env": [self._classify_env(env) for env in sorted(all_required)],
            "repo_manifests": repo_manifests,
        }
        store = self._load_store()
        store["project_env_manifests"][project_id] = manifest
        self._save_store(store)
        return {"ok": True, "mode": "vault_deploy_env_project_manifest", "manifest": manifest}

    def build_readiness_report(
        self,
        project_id: str,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        manifest_result = self.build_project_env_manifest(project_id=project_id, tenant_id=tenant_id)
        if not manifest_result.get("ok"):
            return manifest_result
        manifest = manifest_result["manifest"]
        store = self._load_store()
        secret_presence = store.get("secret_presence", {})

        missing = []
        present = []
        public_env = []
        for env in manifest.get("required_env", []):
            env_name = env["env_name"]
            if env["is_public"]:
                public_env.append(env)
                continue
            key_prefix = f"{tenant_id}:"
            found = any(key.startswith(key_prefix) and key.endswith(f":{env_name}") and item.get("present") for key, item in secret_presence.items())
            if found:
                present.append(env)
            else:
                missing.append(env)

        total_secret = len(present) + len(missing)
        readiness_score = 100 if total_secret == 0 else round((len(present) / total_secret) * 100)
        blockers = [f"Secret em falta: {item['env_name']}" for item in missing]
        report = {
            "report_id": f"deploy-readiness-{uuid4().hex[:12]}",
            "tenant_id": tenant_id,
            "project_id": project_id,
            "project_name": manifest.get("project_name"),
            "created_at": self._now(),
            "status": "ready_for_env_binding" if not blockers else "blocked_missing_secrets",
            "readiness_score": readiness_score,
            "repository_count": manifest.get("repository_count", 0),
            "required_env_count": manifest.get("required_env_count", 0),
            "present_secret_count": len(present),
            "missing_secret_count": len(missing),
            "public_env_count": len(public_env),
            "missing_secrets": missing,
            "present_secrets": present,
            "public_env": public_env,
            "blockers": blockers,
            "approval_steps": [
                {
                    "step_id": "confirm-secret-binding",
                    "label": "Confirmar que os secrets corretos podem ser ligados aos providers de deploy",
                    "approval_required": True,
                },
                {
                    "step_id": "prepare-provider-env-sync",
                    "label": "Preparar sincronização para Vercel/Render/Supabase/GitHub Actions sem expor valores",
                    "approval_required": True,
                },
            ],
            "manifest": manifest,
        }
        store["readiness_reports"].append(report)
        store["readiness_reports"] = store["readiness_reports"][-200:]
        self._save_store(store)
        return {"ok": True, "mode": "vault_deploy_env_readiness_report", "report": report}

    def list_readiness_reports(self, tenant_id: str = "owner-andre", project_id: str | None = None, limit: int = 50) -> Dict[str, Any]:
        store = self._load_store()
        reports = [item for item in store.get("readiness_reports", []) if item.get("tenant_id") == tenant_id]
        if project_id:
            reports = [item for item in reports if item.get("project_id") == project_id]
        reports = reports[-max(min(limit, 200), 1):]
        return {"ok": True, "mode": "vault_deploy_env_readiness_report_list", "report_count": len(reports), "reports": reports}

    def build_dashboard(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        store = self._load_store()
        manifests = [item for item in store.get("project_env_manifests", {}).values() if item.get("tenant_id") == tenant_id]
        reports = self.list_readiness_reports(tenant_id=tenant_id, limit=20).get("reports", [])
        secret_records = [item for item in store.get("secret_presence", {}).values() if item.get("tenant_id") == tenant_id]
        latest_by_project = {}
        for report in reports:
            latest_by_project[report["project_id"]] = report
        return {
            "ok": True,
            "mode": "vault_deploy_env_dashboard",
            "tenant_id": tenant_id,
            "manifest_count": len(manifests),
            "secret_presence_count": len(secret_records),
            "readiness_report_count": len(reports),
            "blocked_project_count": len([item for item in latest_by_project.values() if item.get("status") != "ready_for_env_binding"]),
            "manifests": manifests,
            "recent_reports": reports,
            "secret_presence": secret_records,
        }

    def seed_demo_baribudos_secrets(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        seeded = []
        for secret_name, provider in [
            ("GITHUB_TOKEN", "github"),
            ("VERCEL_TOKEN", "vercel"),
            ("VERCEL_ORG_ID", "vercel"),
            ("SUPABASE_URL", "supabase"),
            ("SUPABASE_ANON_KEY", "supabase"),
        ]:
            seeded.append(self.register_secret_presence(secret_name=secret_name, provider=provider, scope="baribudos-studio", tenant_id=tenant_id)["secret"])
        return {"ok": True, "mode": "vault_deploy_env_seed_demo_baribudos_secrets", "seeded_count": len(seeded), "secrets": seeded}

    def get_package(self) -> Dict[str, Any]:
        return {"ok": True, "mode": "vault_deploy_env_package", "package": {"status": self.get_status(), "dashboard": self.build_dashboard()}}


vault_deploy_env_planner_service = VaultDeployEnvPlannerService()
