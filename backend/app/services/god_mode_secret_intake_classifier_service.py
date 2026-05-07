from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from app.services.god_mode_local_vault_service import god_mode_local_vault_service

PLACEHOLDER_MARKERS = {
    "changeme",
    "change_me",
    "example",
    "sample",
    "dummy",
    "fake",
    "test",
    "todo",
    "your_key_here",
    "your-token-here",
    "paste_here",
    "xxxxx",
    "xxxx",
    "123456",
    "abcdef",
    "placeholder",
}

PROVIDER_RULES = [
    ("github", ["GITHUB", "GH_", "GIT_"], ["repo", "actions", "source_control", "github_api"]),
    ("vercel", ["VERCEL"], ["deploy", "frontend", "domains", "vercel_api"]),
    ("render", ["RENDER"], ["deploy", "backend", "render_api"]),
    ("supabase", ["SUPABASE", "SUPA_"], ["database", "auth", "storage", "supabase_api"]),
    ("openai", ["OPENAI"], ["ai_provider", "chatgpt", "embeddings"]),
    ("anthropic", ["ANTHROPIC", "CLAUDE"], ["ai_provider", "claude"]),
    ("gemini", ["GEMINI", "GOOGLE_AI"], ["ai_provider", "gemini"]),
    ("google_cloud", ["GOOGLE", "GCLOUD", "GCP"], ["cloud", "oauth", "google_api"]),
    ("cloudflare", ["CLOUDFLARE", "CF_"], ["dns", "workers", "cloudflare_api"]),
    ("heygen", ["HEYGEN"], ["video", "avatar", "heygen_api"]),
    ("stripe", ["STRIPE"], ["payments", "billing", "stripe_api"]),
    ("paypal", ["PAYPAL"], ["payments", "billing", "paypal_api"]),
    ("railway", ["RAILWAY"], ["deploy", "backend", "railway_api"]),
    ("database", ["DATABASE_URL", "POSTGRES", "MYSQL", "SQLITE"], ["database", "connection_string"]),
]

SECRET_KEY_HINTS = ["KEY", "TOKEN", "SECRET", "PASSWORD", "PASS", "COOKIE", "PRIVATE", "CLIENT_SECRET", "WEBHOOK_SECRET"]
URL_KEY_HINTS = ["URL", "URI", "ENDPOINT", "DOMAIN", "HOST", "BASE"]


class GodModeSecretIntakeClassifierService:
    SERVICE_ID = "god_mode_secret_intake_classifier"
    VERSION = "phase_205_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "purpose": "Classify pasted env vars, keys, URLs and credentials, store real secrets in the local encrypted vault, and return only vault references.",
            "stores_real_values_in_vault": True,
            "stores_raw_values_in_repo_or_normal_memory": False,
            "detects_placeholders": True,
            "supports_bulk_env_paste": True,
        }

    def ingest_text(
        self,
        text: str,
        project_hint: str = "GOD_MODE",
        default_provider: str = "auto",
        source: str = "mobile_popup_or_operator_paste",
        tenant_id: str = "owner-andre",
        store_real_values: bool = True,
    ) -> Dict[str, Any]:
        entries = self._extract_entries(text)
        classified: List[Dict[str, Any]] = []
        stored: List[Dict[str, Any]] = []
        ignored: List[Dict[str, Any]] = []
        for entry in entries:
            item = self._classify_entry(entry, project_hint=project_hint, default_provider=default_provider, source=source)
            classified.append(item)
            if item["should_store_in_vault"] and store_real_values:
                stored_result = god_mode_local_vault_service.store_secret(
                    raw_secret=item["raw_value_for_vault_only"],
                    label=item["label"],
                    purpose=item["purpose"],
                    secret_kind=item["secret_kind"],
                    provider=item["provider"],
                    project_id=item["project_id"],
                    scope=item["scope"],
                    source_ref={"type": "secret_intake", "source": source, "key": item.get("key", ""), "intake_id": item["intake_item_id"]},
                    reuse_policy=item["reuse_policy"],
                    tenant_id=tenant_id,
                )
                safe_item = self._safe_item(item)
                safe_item["vault_reference"] = stored_result.get("vault_reference")
                stored.append(safe_item)
            else:
                ignored.append(self._safe_item(item))
        return {
            "ok": True,
            "mode": "secret_intake_ingest_text",
            "intake_id": f"secret-intake-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "project_hint": project_hint,
            "source": source,
            "entry_count": len(entries),
            "stored_count": len(stored),
            "ignored_count": len(ignored),
            "stored_vault_references": stored,
            "ignored_or_placeholder": ignored,
            "raw_secret_values_returned": False,
        }

    def plan_needed_token(
        self,
        provider: str,
        purpose: str,
        project_id: str = "GOD_MODE",
        required_scopes: List[str] | None = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        return god_mode_local_vault_service.create_token_generation_plan(
            provider=provider,
            purpose=purpose,
            project_id=project_id,
            required_scopes=required_scopes or self._default_scopes(provider, purpose),
            requested_by="god_mode_secret_intake_classifier",
            storage_label=f"{provider} token for {project_id}: {purpose}",
            source_ref={"type": "token_generation_request", "provider": provider, "purpose": purpose},
            tenant_id=tenant_id,
        )

    def _extract_entries(self, text: str) -> List[Dict[str, str]]:
        entries: List[Dict[str, str]] = []
        for raw_line in (text or "").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            match = re.match(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_\-.]*)\s*=\s*(.*)$", line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip().strip('"').strip("'")
                entries.append({"key": key, "value": value, "source_format": "env_assignment"})
                continue
            url_match = re.search(r"https?://[^\s'\"<>]+", line)
            if url_match:
                entries.append({"key": "URL", "value": url_match.group(0), "source_format": "url_line"})
                continue
            loose = re.match(r"^([A-Za-z0-9_\-. ]{3,80})\s*[:：]\s*(.+)$", line)
            if loose:
                entries.append({"key": loose.group(1).strip().replace(" ", "_"), "value": loose.group(2).strip().strip('"').strip("'"), "source_format": "label_value"})
        return entries

    def _classify_entry(self, entry: Dict[str, str], project_hint: str, default_provider: str, source: str) -> Dict[str, Any]:
        key = entry.get("key", "VALUE")
        value = entry.get("value", "")
        upper_key = key.upper()
        provider = self._infer_provider(upper_key, value, default_provider)
        secret_kind = self._infer_secret_kind(upper_key, value)
        realness = self._realness(value, secret_kind)
        is_secret_like = secret_kind in {"api_key", "token", "password", "cookie", "private_key", "connection_string", "webhook_secret", "credential"}
        should_store = realness == "real_like" and (is_secret_like or secret_kind == "url")
        if secret_kind == "url" and provider == "unknown" and not self._is_service_url(value):
            should_store = False
        purpose_tags = self._purpose_tags(provider, upper_key, secret_kind)
        project_id = self._infer_project(project_hint, key, value)
        item = {
            "intake_item_id": f"secret-intake-item-{uuid4().hex[:12]}",
            "key": key,
            "provider": provider,
            "project_id": project_id,
            "secret_kind": secret_kind,
            "scope": "project" if project_id else "global",
            "purpose": ", ".join(purpose_tags),
            "label": f"{provider}:{project_id}:{key}",
            "realness": realness,
            "should_store_in_vault": should_store,
            "reuse_policy": "reuse_for_same_provider_project_and_purpose",
            "source": source,
            "raw_value_for_vault_only": value,
            "safe_preview": self._preview(value, secret_kind),
            "source_format": entry.get("source_format"),
        }
        return item

    def _infer_provider(self, upper_key: str, value: str, default_provider: str) -> str:
        combined = f"{upper_key} {value}".upper()
        for provider, markers, _tags in PROVIDER_RULES:
            if any(marker in combined for marker in markers):
                return provider
        if default_provider and default_provider != "auto":
            return default_provider
        if "VERCEL" in value.upper():
            return "vercel"
        if "SUPABASE" in value.upper():
            return "supabase"
        if "GITHUB" in value.upper():
            return "github"
        if "RENDER" in value.upper():
            return "render"
        return "unknown"

    def _infer_secret_kind(self, upper_key: str, value: str) -> str:
        if "DATABASE_URL" in upper_key or value.startswith(("postgres://", "postgresql://", "mysql://")):
            return "connection_string"
        if "PRIVATE" in upper_key and "KEY" in upper_key:
            return "private_key"
        if "COOKIE" in upper_key:
            return "cookie"
        if "PASSWORD" in upper_key or upper_key.endswith("_PASS") or "PASS" == upper_key:
            return "password"
        if "WEBHOOK" in upper_key and "SECRET" in upper_key:
            return "webhook_secret"
        if "TOKEN" in upper_key:
            return "token"
        if "SECRET" in upper_key:
            return "credential"
        if "KEY" in upper_key:
            return "api_key"
        if any(hint in upper_key for hint in URL_KEY_HINTS) or value.startswith(("http://", "https://")):
            return "url"
        return "config_value"

    def _realness(self, value: str, secret_kind: str) -> str:
        v = (value or "").strip()
        low = v.lower()
        if not v:
            return "empty"
        if any(marker in low for marker in PLACEHOLDER_MARKERS):
            return "placeholder_or_fictional"
        if re.fullmatch(r"[xX*._\-]{4,}", v):
            return "placeholder_or_masked"
        if v.startswith("${") or v.startswith("<") or v.endswith(">"):  # ${TOKEN} or <TOKEN>
            return "placeholder_or_reference"
        if secret_kind == "url":
            return "real_like" if v.startswith(("http://", "https://", "postgres://", "postgresql://", "mysql://")) else "uncertain"
        if len(v) < 12 and secret_kind not in {"password", "config_value"}:
            return "too_short_or_uncertain"
        if re.search(r"[A-Za-z]", v) and re.search(r"[0-9]", v) and len(v) >= 16:
            return "real_like"
        if len(v) >= 24 and re.fullmatch(r"[A-Za-z0-9_\-\.~:/+=]+", v):
            return "real_like"
        return "uncertain"

    def _purpose_tags(self, provider: str, upper_key: str, secret_kind: str) -> List[str]:
        tags = [secret_kind]
        for rule_provider, _markers, provider_tags in PROVIDER_RULES:
            if rule_provider == provider:
                tags.extend(provider_tags)
        if "DEPLOY" in upper_key:
            tags.append("deploy")
        if "BUILD" in upper_key:
            tags.append("build")
        if "DATABASE" in upper_key or "DB" in upper_key:
            tags.append("database")
        return list(dict.fromkeys(tags))

    def _infer_project(self, project_hint: str, key: str, value: str) -> str:
        hint = (project_hint or "GOD_MODE").strip()
        if hint and hint != "auto":
            return hint
        combined = f"{key} {value}".lower()
        if "baribudos" in combined:
            return "BARIBUDOS"
        if "proventil" in combined:
            return "PROVENTIL"
        if "god" in combined or "devops-god-mode" in combined:
            return "GOD_MODE"
        return "UNKNOWN_PROJECT"

    def _preview(self, value: str, secret_kind: str) -> str:
        if secret_kind == "url":
            return value[:100]
        if len(value) <= 8:
            return "***"
        return f"{value[:4]}...{value[-4:]}"

    def _is_service_url(self, value: str) -> bool:
        return value.startswith(("http://", "https://", "postgres://", "postgresql://", "mysql://"))

    def _safe_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in item.items() if key != "raw_value_for_vault_only"}

    def _default_scopes(self, provider: str, purpose: str) -> List[str]:
        p = provider.lower()
        if p == "github":
            return ["repo", "workflow"] if "workflow" in purpose.lower() else ["repo"]
        if p == "vercel":
            return ["deployments", "projects", "env"]
        if p == "render":
            return ["services", "deploy"]
        if p == "supabase":
            return ["project", "database", "auth"]
        return ["minimum_required"]


god_mode_secret_intake_classifier_service = GodModeSecretIntakeClassifierService()
