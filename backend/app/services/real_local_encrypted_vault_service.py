from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.operator_approval_gate_service import operator_approval_gate_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
VAULT_DIR = DATA_DIR / "local_encrypted_vault"
VAULT_INDEX_FILE = VAULT_DIR / "vault_index.json"
VAULT_AUDIT_FILE = VAULT_DIR / "vault_audit.json"

VAULT_INDEX_STORE = AtomicJsonStore(
    VAULT_INDEX_FILE,
    default_factory=lambda: {
        "version": 1,
        "vault_kind": "local_pc_encrypted_value_store",
        "entries": [],
        "unlock_sessions": [],
    },
)
VAULT_AUDIT_STORE = AtomicJsonStore(
    VAULT_AUDIT_FILE,
    default_factory=lambda: {"version": 1, "events": []},
)

PBKDF2_ITERATIONS = 240_000
NONCE_LENGTH = 16
SALT_LENGTH = 16
KEY_LENGTH = 32


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RealLocalEncryptedVaultService:
    """Local encrypted value store for PC runtime.

    This is a local-first vault layer. It stores encrypted values on disk and
    stores only redacted metadata/audit details in JSON. The passphrase is never
    persisted; callers must provide it at store/read time or use a future OS
    keyring/DPAPI layer.

    Cipher construction: PBKDF2-HMAC-SHA256 + HMAC-SHA256 keystream XOR + HMAC
    authentication. This is intentionally dependency-free for Windows artifact
    stability. Future phase can replace it with DPAPI/Fernet/OS keyring.
    """

    SERVICE_ID = "real_local_encrypted_vault"
    VERSION = "phase_184_v1"

    def status(self) -> Dict[str, Any]:
        index = VAULT_INDEX_STORE.load()
        audit = VAULT_AUDIT_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": _now(),
            "vault_dir": str(VAULT_DIR),
            "index_file": str(VAULT_INDEX_FILE),
            "audit_file": str(VAULT_AUDIT_FILE),
            "entry_count": len(index.get("entries", [])),
            "audit_event_count": len(audit.get("events", [])),
            "stores_encrypted_values": True,
            "stores_plaintext_values": False,
            "passphrase_persisted": False,
            "approval_required_for_read": True,
            "approval_required_for_write": True,
            "cipher": "PBKDF2-HMAC-SHA256 + authenticated stream XOR",
        }

    def policy(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "policy": {
                "principle": "Raw secret values stay encrypted on the PC and are never written to GitHub, AndreOS memory, Obsidian cloud, logs or external AI context.",
                "write_requires": ["operator approval gate", "local passphrase", "redacted audit"],
                "read_requires": ["operator approval gate", "local passphrase", "purpose", "redacted audit"],
                "stored_plaintext": [],
                "stored_metadata": ["secret_ref_id", "project_id", "provider", "environment", "key_name", "fingerprint", "cipher_file", "created_at", "updated_at"],
                "blocked": ["return raw secret in status/package/list endpoints", "persist passphrase", "commit vault data", "send value to external AI"],
                "future_hardening": ["Windows DPAPI", "OS keyring", "hardware backed unlock", "time-limited mobile approval token", "vault rotation"],
            },
        }

    def create_write_gate(
        self,
        secret_ref_id: str,
        project_id: str,
        provider: str,
        environment: str,
        key_name: str,
        risk_level: str = "high",
    ) -> Dict[str, Any]:
        summary = f"Store encrypted secret ref={secret_ref_id} project={project_id} provider={provider} env={environment} key={key_name}"
        gate = operator_approval_gate_service.create_gate(
            tenant_id="GOD_MODE",
            thread_id="local-encrypted-vault",
            action_label="Store encrypted local vault secret",
            action_scope="local_pc_vault_write",
            action_payload_summary=summary,
            risk_level=risk_level,
        )
        self._audit("write_gate_created", secret_ref_id, project_id, provider, environment, {"gate_id": gate.get("gate", {}).get("gate_id"), "key_name": key_name})
        return gate

    def create_read_gate(
        self,
        secret_ref_id: str,
        purpose: str,
        risk_level: str = "high",
    ) -> Dict[str, Any]:
        summary = f"Read/decrypt local vault secret ref={secret_ref_id} purpose={purpose[:200]}"
        gate = operator_approval_gate_service.create_gate(
            tenant_id="GOD_MODE",
            thread_id="local-encrypted-vault",
            action_label="Read encrypted local vault secret",
            action_scope="local_pc_vault_read",
            action_payload_summary=summary,
            risk_level=risk_level,
        )
        self._audit("read_gate_created", secret_ref_id, "UNKNOWN", "UNKNOWN", "UNKNOWN", {"gate_id": gate.get("gate", {}).get("gate_id"), "purpose": purpose[:300]})
        return gate

    def store_secret(
        self,
        secret_ref_id: str,
        secret_value: str,
        passphrase: str,
        project_id: str,
        provider: str,
        environment: str,
        key_name: str,
        approved_gate_id: str,
        notes: str | None = None,
    ) -> Dict[str, Any]:
        gate_status = self._gate_approved(approved_gate_id)
        if not gate_status["ok"]:
            self._audit("write_blocked_gate_not_approved", secret_ref_id, project_id, provider, environment, {"gate_id": approved_gate_id})
            return gate_status
        if not passphrase:
            return {"ok": False, "mode": "vault_store_result", "error": "passphrase_required"}
        if not secret_value:
            return {"ok": False, "mode": "vault_store_result", "error": "secret_value_required"}

        secret_ref_id = self._safe_ref(secret_ref_id)
        cipher = self._encrypt(secret_value, passphrase)
        cipher_file = VAULT_DIR / f"{secret_ref_id}.vault"
        cipher_file.parent.mkdir(parents=True, exist_ok=True)
        cipher_file.write_text(cipher["payload"], encoding="utf-8")

        fingerprint = self._fingerprint(secret_value)
        metadata = {
            "secret_ref_id": secret_ref_id,
            "project_id": self._safe_text(project_id),
            "provider": self._safe_text(provider),
            "environment": self._safe_text(environment),
            "key_name": self._safe_text(key_name),
            "fingerprint": fingerprint,
            "value_length": len(secret_value),
            "cipher_file": str(cipher_file),
            "algorithm": cipher["algorithm"],
            "kdf_iterations": PBKDF2_ITERATIONS,
            "has_encrypted_value": True,
            "notes": (notes or "")[:1000],
            "created_at": _now(),
            "updated_at": _now(),
            "last_write_gate_id": approved_gate_id,
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            entries = [item for item in state.get("entries", []) if item.get("secret_ref_id") != secret_ref_id]
            entries.append(metadata)
            state["entries"] = entries[-1000:]
            return state

        VAULT_INDEX_STORE.update(mutate)
        self._audit("secret_stored_encrypted", secret_ref_id, project_id, provider, environment, {"gate_id": approved_gate_id, "key_name": key_name, "value_length": len(secret_value)})
        return {
            "ok": True,
            "mode": "vault_store_result",
            "secret_ref_id": secret_ref_id,
            "metadata": self._redact_entry(metadata),
            "stores_plaintext_values": False,
        }

    def read_secret(
        self,
        secret_ref_id: str,
        passphrase: str,
        approved_gate_id: str,
        purpose: str,
        reveal: bool = False,
    ) -> Dict[str, Any]:
        gate_status = self._gate_approved(approved_gate_id)
        if not gate_status["ok"]:
            self._audit("read_blocked_gate_not_approved", secret_ref_id, "UNKNOWN", "UNKNOWN", "UNKNOWN", {"gate_id": approved_gate_id, "purpose": purpose[:300]})
            return gate_status
        entry = self._find_entry(secret_ref_id)
        if entry is None:
            return {"ok": False, "mode": "vault_read_result", "error": "secret_ref_not_found", "secret_ref_id": secret_ref_id}
        cipher_file = Path(entry["cipher_file"])
        if not cipher_file.exists():
            return {"ok": False, "mode": "vault_read_result", "error": "cipher_file_not_found", "secret_ref_id": secret_ref_id}
        try:
            plaintext = self._decrypt(cipher_file.read_text(encoding="utf-8"), passphrase)
        except Exception:
            self._audit("read_failed_decrypt", secret_ref_id, entry.get("project_id"), entry.get("provider"), entry.get("environment"), {"gate_id": approved_gate_id, "purpose": purpose[:300]})
            return {"ok": False, "mode": "vault_read_result", "error": "decrypt_failed_or_wrong_passphrase", "secret_ref_id": secret_ref_id}

        fingerprint = self._fingerprint(plaintext)
        if fingerprint != entry.get("fingerprint"):
            return {"ok": False, "mode": "vault_read_result", "error": "fingerprint_mismatch", "secret_ref_id": secret_ref_id}

        self._audit("secret_decrypted_for_local_use", secret_ref_id, entry.get("project_id"), entry.get("provider"), entry.get("environment"), {"gate_id": approved_gate_id, "purpose": purpose[:300], "revealed_to_response": bool(reveal)})
        result: Dict[str, Any] = {
            "ok": True,
            "mode": "vault_read_result",
            "secret_ref_id": secret_ref_id,
            "metadata": self._redact_entry(entry),
            "value_available_for_local_injection": True,
            "value_length": len(plaintext),
            "value_preview": self._preview(plaintext),
            "revealed": bool(reveal),
        }
        if reveal:
            result["secret_value"] = plaintext
        return result

    def list_entries(self) -> Dict[str, Any]:
        index = VAULT_INDEX_STORE.load()
        entries = [self._redact_entry(item) for item in index.get("entries", [])]
        return {"ok": True, "mode": "vault_entries", "entry_count": len(entries), "entries": entries}

    def audit_log(self, limit: int = 50) -> Dict[str, Any]:
        audit = VAULT_AUDIT_STORE.load()
        events = list(reversed(audit.get("events", [])))[0:max(1, min(limit, 200))]
        return {"ok": True, "mode": "vault_audit", "event_count": len(events), "events": events}

    def package(self) -> Dict[str, Any]:
        return {
            "status": self.status(),
            "policy": self.policy(),
            "entries": self.list_entries(),
            "audit_recent": self.audit_log(limit=20),
            "approval_gate_package": operator_approval_gate_service.get_package(),
            "operational_routes": {
                "create_write_gate": "/api/real-local-encrypted-vault/create-write-gate",
                "store_secret": "/api/real-local-encrypted-vault/store-secret",
                "create_read_gate": "/api/real-local-encrypted-vault/create-read-gate",
                "read_secret": "/api/real-local-encrypted-vault/read-secret",
            },
        }

    def _safe_ref(self, value: str) -> str:
        cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in (value or "").strip())
        return cleaned[:160] or f"secret-ref-{uuid4().hex[:12]}"

    def _safe_text(self, value: str) -> str:
        return (value or "UNKNOWN").strip()[:300]

    def _fingerprint(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()

    def _derive_keys(self, passphrase: str, salt: bytes) -> tuple[bytes, bytes]:
        material = hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=KEY_LENGTH * 2)
        return material[:KEY_LENGTH], material[KEY_LENGTH:]

    def _keystream(self, key: bytes, nonce: bytes, length: int) -> bytes:
        out = bytearray()
        counter = 0
        while len(out) < length:
            out.extend(hmac.new(key, nonce + counter.to_bytes(8, "big"), hashlib.sha256).digest())
            counter += 1
        return bytes(out[:length])

    def _encrypt(self, plaintext: str, passphrase: str) -> Dict[str, str]:
        salt = os.urandom(SALT_LENGTH)
        nonce = os.urandom(NONCE_LENGTH)
        enc_key, auth_key = self._derive_keys(passphrase, salt)
        plain = plaintext.encode("utf-8")
        stream = self._keystream(enc_key, nonce, len(plain))
        ciphertext = bytes(a ^ b for a, b in zip(plain, stream))
        mac = hmac.new(auth_key, salt + nonce + ciphertext, hashlib.sha256).digest()
        blob = b"GMV1" + salt + nonce + mac + ciphertext
        return {"algorithm": "GMV1-PBKDF2-HMAC-SHA256-XOR-HMAC", "payload": base64.urlsafe_b64encode(blob).decode("ascii")}

    def _decrypt(self, encoded: str, passphrase: str) -> str:
        blob = base64.urlsafe_b64decode(encoded.encode("ascii"))
        if not blob.startswith(b"GMV1"):
            raise ValueError("unsupported_vault_blob")
        offset = 4
        salt = blob[offset:offset + SALT_LENGTH]
        offset += SALT_LENGTH
        nonce = blob[offset:offset + NONCE_LENGTH]
        offset += NONCE_LENGTH
        mac = blob[offset:offset + 32]
        offset += 32
        ciphertext = blob[offset:]
        enc_key, auth_key = self._derive_keys(passphrase, salt)
        expected_mac = hmac.new(auth_key, salt + nonce + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("vault_mac_mismatch")
        stream = self._keystream(enc_key, nonce, len(ciphertext))
        plain = bytes(a ^ b for a, b in zip(ciphertext, stream))
        return plain.decode("utf-8")

    def _find_entry(self, secret_ref_id: str) -> Dict[str, Any] | None:
        target = self._safe_ref(secret_ref_id)
        index = VAULT_INDEX_STORE.load()
        return next((item for item in index.get("entries", []) if item.get("secret_ref_id") == target), None)

    def _redact_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(entry)
        safe.pop("secret_value", None)
        return safe

    def _preview(self, value: str) -> str:
        if not value:
            return ""
        if len(value) <= 6:
            return "***"
        return f"{value[:2]}***{value[-2:]}"

    def _gate_approved(self, gate_id: str) -> Dict[str, Any]:
        gates = operator_approval_gate_service.list_gates(thread_id="local-encrypted-vault").get("gates", [])
        gate = next((item for item in gates if item.get("gate_id") == gate_id), None)
        if gate is None:
            return {"ok": False, "mode": "vault_gate_check", "error": "approval_gate_not_found", "gate_id": gate_id}
        if gate.get("status") != "approved":
            return {"ok": False, "mode": "vault_gate_check", "error": "approval_gate_not_approved", "gate_id": gate_id, "gate_status": gate.get("status")}
        return {"ok": True, "mode": "vault_gate_check", "gate_id": gate_id, "gate_status": "approved"}

    def _audit(self, event_type: str, secret_ref_id: str, project_id: str | None, provider: str | None, environment: str | None, details: Dict[str, Any] | None = None) -> None:
        event = {
            "event_id": f"vault-event-{uuid4().hex[:12]}",
            "event_type": event_type,
            "created_at": _now(),
            "secret_ref_id": self._safe_ref(secret_ref_id or "UNKNOWN"),
            "project_id": self._safe_text(project_id or "UNKNOWN"),
            "provider": self._safe_text(provider or "UNKNOWN"),
            "environment": self._safe_text(environment or "UNKNOWN"),
            "details": details or {},
            "redacted": True,
        }

        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            events: List[Dict[str, Any]] = state.get("events", [])
            events.append(event)
            state["events"] = events[-1000:]
            return state

        VAULT_AUDIT_STORE.update(mutate)


real_local_encrypted_vault_service = RealLocalEncryptedVaultService()
