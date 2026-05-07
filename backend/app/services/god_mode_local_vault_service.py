from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.utils.atomic_json_store import AtomicJsonStore

PRIVATE_DATA_DIR = Path("data") / "private"
VAULT_FILE = PRIVATE_DATA_DIR / "god_mode_local_vault.json"
KEY_FILE = PRIVATE_DATA_DIR / "god_mode_local_vault.key"

VAULT_STORE = AtomicJsonStore(
    VAULT_FILE,
    default_factory=lambda: {"version": 1, "vault_items": [], "token_generation_plans": [], "audit_log": []},
)


class GodModeLocalVaultService:
    SERVICE_ID = "god_mode_local_vault"
    VERSION = "phase_205_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = VAULT_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "vault_file": str(VAULT_FILE),
            "key_file": str(KEY_FILE),
            "vault_item_count": len(state.get("vault_items", [])),
            "token_generation_plan_count": len(state.get("token_generation_plans", [])),
            "raw_secret_values_exposed_in_api": False,
            "raw_secret_values_allowed_in_repo": False,
            "stores_encrypted_values_locally": True,
            "requires_oner_or_gate_for_reveal": True,
        }

    def store_secret(
        self,
        *,
        raw_secret: str,
        label: str,
        purpose: str,
        secret_kind: str = "credential",
        provider: str = "manual",
        project_id: str = "GOD_MODE",
        scope: str = "project",
        source_ref: Dict[str, Any] | None = None,
        reuse_policy: str = "reuse_for_same_provider_project_and_purpose",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        if raw_secret is None or str(raw_secret) == "":
            return {"ok": False, "mode": "vault_store_secret", "error": "empty_secret_not_stored"}
        encrypted = self._encrypt(str(raw_secret))
        item = {
            "vault_item_id": f"vault-item-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "updated_at": self._now(),
            "tenant_id": tenant_id,
            "project_id": self._clean(project_id)[:120],
            "label": self._clean(label)[:160],
            "purpose": self._clean(purpose)[:500],
            "secret_kind": self._clean(secret_kind)[:80],
            "provider": self._clean(provider)[:120],
            "scope": self._clean(scope)[:120],
            "source_ref": self._safe_source_ref(source_ref or {}),
            "reuse_policy": self._clean(reuse_policy)[:200],
            "status": "active",
            "encryption": encrypted,
            "fingerprint": self._fingerprint(str(raw_secret)),
            "raw_value_stored": False,
            "raw_value_exposed": False,
        }
        self._store("vault_items", item)
        self._audit("store_secret", item["vault_item_id"], f"stored {item['secret_kind']} for {item['provider']} / {item['purpose']}", tenant_id)
        return {"ok": True, "mode": "vault_store_secret", "vault_reference": self._reference(item)}

    def build_reference_without_value(
        self,
        *,
        label: str,
        purpose: str,
        secret_kind: str = "credential",
        provider: str = "manual",
        project_id: str = "GOD_MODE",
        source_ref: Dict[str, Any] | None = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        ref = {
            "vault_reference_id": f"vault-ref-pending-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "project_id": self._clean(project_id)[:120],
            "label": self._clean(label)[:160],
            "purpose": self._clean(purpose)[:500],
            "secret_kind": self._clean(secret_kind)[:80],
            "provider": self._clean(provider)[:120],
            "source_ref": self._safe_source_ref(source_ref or {}),
            "status": "pending_value",
            "raw_value_stored": False,
            "raw_value_exposed": False,
        }
        return {"ok": True, "mode": "vault_pending_reference", "vault_reference": ref}

    def list_references(self, provider: str | None = None, project_id: str | None = None, limit: int = 100) -> Dict[str, Any]:
        items = list(VAULT_STORE.load().get("vault_items", []))
        if provider:
            items = [item for item in items if item.get("provider") == provider]
        if project_id:
            items = [item for item in items if item.get("project_id") == project_id]
        refs = [self._reference(item) for item in items[-max(1, min(limit, 500)):]]
        return {"ok": True, "mode": "vault_reference_list", "count": len(refs), "vault_references": refs}

    def create_token_generation_plan(
        self,
        *,
        provider: str,
        purpose: str,
        project_id: str = "GOD_MODE",
        required_scopes: List[str] | None = None,
        requested_by: str = "god_mode",
        storage_label: str | None = None,
        source_ref: Dict[str, Any] | None = None,
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        plan = {
            "token_generation_plan_id": f"token-plan-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "provider": self._clean(provider)[:120],
            "project_id": self._clean(project_id)[:120],
            "purpose": self._clean(purpose)[:500],
            "required_scopes": [self._clean(scope)[:120] for scope in (required_scopes or [])[:25]],
            "requested_by": self._clean(requested_by)[:120],
            "storage_label": self._clean(storage_label or f"{provider} token for {project_id}")[:160],
            "source_ref": self._safe_source_ref(source_ref or {}),
            "status": "needs_oner_or_provider_gate",
            "steps": [
                "Confirm the provider and exact purpose.",
                "Request only the minimum scopes needed.",
                "Open provider/token creation flow only through an approved gate.",
                "Store the generated token in the local encrypted vault.",
                "Expose only a vault reference to other God Mode modules.",
            ],
            "can_generate_without_oner_gate": False,
            "can_store_raw_token_in_repo_or_memory": False,
        }
        self._store("token_generation_plans", plan)
        self._audit("create_token_generation_plan", plan["token_generation_plan_id"], f"provider={provider} purpose={purpose}", tenant_id)
        return {"ok": True, "mode": "token_generation_plan", "token_generation_plan": plan}

    def reveal_for_runtime(self, vault_item_id: str, approved_gate_id: str | None = None, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        if not approved_gate_id:
            return {"ok": False, "mode": "vault_reveal_for_runtime", "error": "approved_gate_required", "raw_secret_returned": False}
        item = self._find(vault_item_id)
        if not item:
            return {"ok": False, "mode": "vault_reveal_for_runtime", "error": "vault_item_not_found", "raw_secret_returned": False}
        raw = self._decrypt(item.get("encryption", {}))
        self._audit("reveal_for_runtime", vault_item_id, f"approved_gate_id={approved_gate_id}", tenant_id)
        return {"ok": True, "mode": "vault_reveal_for_runtime", "vault_item_id": vault_item_id, "secret_value": raw, "raw_secret_returned": True, "warning": "Use only in backend runtime; never log or persist outside the vault."}

    def _reference(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "vault_item_id": item.get("vault_item_id"),
            "tenant_id": item.get("tenant_id"),
            "project_id": item.get("project_id"),
            "label": item.get("label"),
            "purpose": item.get("purpose"),
            "secret_kind": item.get("secret_kind"),
            "provider": item.get("provider"),
            "scope": item.get("scope"),
            "reuse_policy": item.get("reuse_policy"),
            "status": item.get("status"),
            "fingerprint": item.get("fingerprint"),
            "raw_value_stored": False,
            "raw_value_exposed": False,
        }

    def _encrypt(self, text: str) -> Dict[str, str]:
        key = self._load_or_create_key()
        salt = os.urandom(16)
        nonce = os.urandom(16)
        enc_key = hashlib.pbkdf2_hmac("sha256", key, salt, 200_000, dklen=32)
        data = text.encode("utf-8")
        stream = self._keystream(enc_key, nonce, len(data))
        cipher = bytes(a ^ b for a, b in zip(data, stream))
        tag = hmac.new(enc_key, b"god-mode-vault-v1" + nonce + cipher, hashlib.sha256).digest()
        return {
            "algorithm": "local_hmac_stream_v1",
            "salt": base64.b64encode(salt).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "ciphertext": base64.b64encode(cipher).decode("ascii"),
            "tag": base64.b64encode(tag).decode("ascii"),
        }

    def _decrypt(self, payload: Dict[str, str]) -> str:
        key = self._load_or_create_key()
        salt = base64.b64decode(payload.get("salt", ""))
        nonce = base64.b64decode(payload.get("nonce", ""))
        cipher = base64.b64decode(payload.get("ciphertext", ""))
        tag = base64.b64decode(payload.get("tag", ""))
        enc_key = hashlib.pbkdf2_hmac("sha256", key, salt, 200_000, dklen=32)
        expected = hmac.new(enc_key, b"god-mode-vault-v1" + nonce + cipher, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected):
            raise ValueError("vault_integrity_check_failed")
        stream = self._keystream(enc_key, nonce, len(cipher))
        data = bytes(a ^ b for a, b in zip(cipher, stream))
        return data.decode("utf-8")

    def _keystream(self, key: bytes, nonce: bytes, size: int) -> bytes:
        out = bytearray()
        counter = 0
        while len(out) < size:
            out.extend(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
            counter += 1
        return bytes(out[:size])

    def _load_or_create_key(self) -> bytes:
        PRIVATE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        if KEY_FILE.exists():
            return base64.b64decode(KEY_FILE.read_text(encoding="utf-8").strip())
        key = os.urandom(32)
        KEY_FILE.write_text(base64.b64encode(key).decode("ascii"), encoding="utf-8")
        try:
            os.chmod(KEY_FILE, 0o600)
        except Exception:
            pass
        return key

    def _fingerprint(self, value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"sha256:{digest[:16]}"

    def _find(self, vault_item_id: str) -> Dict[str, Any] | None:
        return next((item for item in VAULT_STORE.load().get("vault_items", []) if item.get("vault_item_id") == vault_item_id), None)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-2000:]
            return state
        VAULT_STORE.update(mutate)

    def _audit(self, action: str, item_id: str, detail: str, tenant_id: str) -> None:
        self._store("audit_log", {"created_at": self._now(), "tenant_id": tenant_id, "action": action, "item_id": item_id, "detail": self._clean(detail)[:500]})

    def _safe_source_ref(self, source_ref: Dict[str, Any]) -> Dict[str, Any]:
        safe: Dict[str, Any] = {}
        for key, value in source_ref.items():
            clean_key = re.sub(r"[^A-Za-z0-9_\-]+", "_", str(key))[:80]
            safe[clean_key] = self._clean(str(value))[:500]
        return safe

    def _clean(self, value: str) -> str:
        lines = []
        for line in (value or "").splitlines():
            lowered = line.lower()
            if any(key in lowered for key in ["api_key=", "token=", "password=", "cookie=", "secret=", "private_key="]):
                lines.append("[REDACTED_SECRET_LINE]")
            else:
                lines.append(line)
        return "\n".join(lines).strip()


god_mode_local_vault_service = GodModeLocalVaultService()
