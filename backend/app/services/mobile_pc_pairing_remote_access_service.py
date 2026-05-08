from __future__ import annotations

import base64
import json
import os
import socket
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.services.god_mode_local_vault_service import god_mode_local_vault_service
from app.services.mobile_permission_relay_driver_voice_service import mobile_permission_relay_driver_voice_service
from app.utils.atomic_json_store import AtomicJsonStore

DATA_DIR = Path("data")
PAIRING_FILE = DATA_DIR / "mobile_pc_pairing_remote_access.json"
PAIRING_STORE = AtomicJsonStore(
    PAIRING_FILE,
    default_factory=lambda: {"version": 1, "pairing_sessions": [], "remote_profiles": [], "connection_events": []},
)

REMOTE_PROVIDERS = ["cloudflare_tunnel", "tailscale", "ngrok", "manual_public_url"]
KNOWN_HOME_PC_IPS = ["192.168.1.81"]
KNOWN_HOME_PHONE_IPS = ["192.168.1.47"]
LAN_SWEEP_BASE_IP = "192.168.1.81"
LAN_SWEEP_RADIUS = 20
LAN_SWEEP_PORT = 8787


class MobilePcPairingRemoteAccessService:
    SERVICE_ID = "mobile_pc_pairing_remote_access"
    VERSION = "phase_209_v1"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def status(self) -> Dict[str, Any]:
        state = PAIRING_STORE.load()
        return {
            "ok": True,
            "service": self.SERVICE_ID,
            "version": self.VERSION,
            "generated_at": self._now(),
            "known_home_pc_ips": KNOWN_HOME_PC_IPS,
            "known_home_phone_ips": KNOWN_HOME_PHONE_IPS,
            "lan_sweep_base_ip": LAN_SWEEP_BASE_IP,
            "lan_sweep_radius": LAN_SWEEP_RADIUS,
            "lan_sweep_range": self._lan_sweep_range(),
            "pairing_session_count": len(state.get("pairing_sessions", [])),
            "remote_profile_count": len(state.get("remote_profiles", [])),
            "supports_home_auto_pairing": True,
            "supports_lan_sweep_candidates": True,
            "supports_remote_access_contract": True,
            "remote_access_requires_provider_or_public_url": True,
            "stores_remote_secrets_in_vault": True,
        }

    def create_pairing_session(self, tenant_id: str = "owner-andre", port: int = 8787, ttl_minutes: int = 30) -> Dict[str, Any]:
        local_ips = self._local_ips()
        lan_candidates = self.lan_scan_candidates(port=port).get("lan_candidates", [])
        session_id = f"pairing-{uuid4().hex[:12]}"
        pairing_code = base64.urlsafe_b64encode(os.urandom(9)).decode("ascii").rstrip("=")
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=max(5, min(ttl_minutes, 1440)))).isoformat()
        urls = self._dedupe([item["url"] for item in lan_candidates] + [f"http://{ip}:{port}/app/mobile-permission-relay" for ip in local_ips])
        manifest = {
            "pairing_session_id": session_id,
            "pairing_code": pairing_code,
            "tenant_id": tenant_id,
            "created_at": self._now(),
            "expires_at": expires_at,
            "pc_name": socket.gethostname(),
            "known_home_pc_ips": KNOWN_HOME_PC_IPS,
            "known_home_phone_ips": KNOWN_HOME_PHONE_IPS,
            "lan_sweep_base_ip": LAN_SWEEP_BASE_IP,
            "lan_sweep_radius": LAN_SWEEP_RADIUS,
            "lan_sweep_range": self._lan_sweep_range(),
            "lan_candidates": lan_candidates,
            "local_ips": local_ips,
            "port": port,
            "home_urls": urls,
            "recommended_mobile_routes": [
                "/app/mobile-permission-relay",
                "/app/driver-voice-permissions",
                "/app/today-ready",
                "/app/ia-operator-bridge",
                "/app/god-mode-vault",
                "/app/mobile-pc-pairing",
            ],
            "qr_payload": json.dumps({"type": "god_mode_pairing", "pairing_session_id": session_id, "code": pairing_code, "urls": urls, "lan_candidates": lan_candidates, "known_home_pc_ips": KNOWN_HOME_PC_IPS, "known_home_phone_ips": KNOWN_HOME_PHONE_IPS}, ensure_ascii=False),
            "status": "active",
            "remote_profile_id": None,
        }
        self._store("pairing_sessions", manifest)
        return {"ok": True, "mode": "create_pairing_session", "pairing_session": manifest}

    def lan_scan_candidates(self, port: int = LAN_SWEEP_PORT) -> Dict[str, Any]:
        ip_order = self._lan_sweep_ips()
        candidates = []
        for rank, ip in enumerate(ip_order, start=1):
            candidates.append({
                "rank": rank,
                "ip": ip,
                "url": f"http://{ip}:{port}/app/mobile-permission-relay",
                "health_url": f"http://{ip}:{port}/api/health",
                "mode": "home_lan_sweep",
                "priority": self._candidate_priority(ip),
                "reason": self._candidate_reason(ip),
            })
        return {
            "ok": True,
            "mode": "lan_scan_candidates",
            "base_ip": LAN_SWEEP_BASE_IP,
            "radius": LAN_SWEEP_RADIUS,
            "range": self._lan_sweep_range(),
            "known_home_pc_ips": KNOWN_HOME_PC_IPS,
            "known_home_phone_ips": KNOWN_HOME_PHONE_IPS,
            "candidate_count": len(candidates),
            "lan_candidates": candidates,
        }

    def create_remote_access_plan(
        self,
        provider: str = "tailscale",
        public_url: str = "",
        project_id: str = "GOD_MODE",
        tenant_id: str = "owner-andre",
    ) -> Dict[str, Any]:
        provider = provider if provider in REMOTE_PROVIDERS else "manual_public_url"
        profile = {
            "remote_profile_id": f"remote-profile-{uuid4().hex[:12]}",
            "created_at": self._now(),
            "tenant_id": tenant_id,
            "project_id": project_id,
            "provider": provider,
            "public_url": public_url.strip(),
            "status": "ready" if public_url.strip().startswith("https://") else "needs_setup",
            "vault_reference_ids": [],
            "mobile_entry_url": f"{public_url.rstrip('/')}/app/mobile-permission-relay" if public_url.strip().startswith("https://") else "",
            "steps": self._remote_steps(provider),
            "recommendation": self._remote_recommendation(provider),
            "security": {
                "requires_oner_gate": True,
                "store_provider_material_in_vault": True,
                "do_not_commit_remote_material": True,
                "recommended": "Use HTTPS tunnel or private mesh network. Keep PC awake while using remote cockpit.",
            },
        }
        self._store("remote_profiles", profile)
        if not profile["public_url"]:
            permission = mobile_permission_relay_driver_voice_service.create_permission_request(
                title=f"Configurar acesso remoto {provider}",
                body="Para comandar o God Mode da rua, o PC precisa de um endereço remoto seguro. Recomendo Tailscale para uso rápido sem abrir portas no router. Cloudflare Tunnel fica melhor quando quiseres URL/domain estável.",
                request_type="sensitive_fill",
                project_id=project_id,
                source_ref={"type": "remote_access_profile", "remote_profile_id": profile["remote_profile_id"], "provider": provider},
                priority="high",
                requires_sensitive_input=True,
                form_schema=[{"name": "remote_public_url", "label": "URL HTTPS remota ou dados do acesso remoto", "type": "text", "required": True, "sensitive": True}],
                wait_for_response=True,
                tenant_id=tenant_id,
            )
        else:
            permission = None
        return {"ok": True, "mode": "create_remote_access_plan", "remote_profile": profile, "permission_request": permission}

    def store_remote_material(self, remote_profile_id: str, material: str, label: str = "remote access material", tenant_id: str = "owner-andre") -> Dict[str, Any]:
        profile = self._find("remote_profiles", "remote_profile_id", remote_profile_id)
        if not profile:
            return {"ok": False, "error": "remote_profile_not_found", "remote_profile_id": remote_profile_id}
        stored = god_mode_local_vault_service.store_secret(
            raw_secret=material,
            label=f"{profile.get('provider')}:{profile.get('project_id')}:{label}",
            purpose=f"Remote access for God Mode mobile cockpit via {profile.get('provider')}",
            secret_kind="remote_access_material",
            provider=str(profile.get("provider")),
            project_id=str(profile.get("project_id")),
            scope="device_pairing",
            source_ref={"type": "mobile_pc_pairing_remote_access", "remote_profile_id": remote_profile_id},
            reuse_policy="reuse_for_same_pc_remote_access",
            tenant_id=tenant_id,
        )
        ref = stored.get("vault_reference")
        if ref:
            self._patch_remote_profile(remote_profile_id, {"vault_reference_ids": list(set((profile.get("vault_reference_ids") or []) + [ref.get("vault_item_id")]))})
        return {"ok": True, "mode": "store_remote_material", "vault_reference": ref, "remote_profile": self._find("remote_profiles", "remote_profile_id", remote_profile_id)}

    def _refresh_tailscale_profile(self, tenant_id: str) -> None:
        try:
            from app.services.private_tunnel_center_service import private_tunnel_center_service
            report = private_tunnel_center_service.build_tunnel_report(include_pairing=False)
            tailscale_provider = next((p for p in report.get("providers", []) if p.get("provider_id") == "tailscale"), None)
            tailscale_ip = (tailscale_provider or {}).get("detected_ip")
            if tailscale_ip:
                public_url = f"http://{tailscale_ip}:{LAN_SWEEP_PORT}"
                state = PAIRING_STORE.load()
                existing = next((p for p in state.get("remote_profiles", []) if p.get("tenant_id") == tenant_id and p.get("provider") == "tailscale"), None)
                if existing:
                    if existing.get("public_url") != public_url:
                        self._patch_remote_profile(existing["remote_profile_id"], {"public_url": public_url, "status": "ready", "mobile_entry_url": f"{public_url}/app/home"})
                else:
                    self.create_remote_access_plan(provider="tailscale", public_url=public_url, tenant_id=tenant_id)
        except Exception:
            pass

    def connection_manifest(self, tenant_id: str = "owner-andre") -> Dict[str, Any]:
        self._refresh_tailscale_profile(tenant_id)
        state = PAIRING_STORE.load()
        sessions = [s for s in state.get("pairing_sessions", []) if s.get("tenant_id") == tenant_id and s.get("status") == "active"]
        profiles = [p for p in state.get("remote_profiles", []) if p.get("tenant_id") == tenant_id]
        latest_session = sessions[-1] if sessions else self.create_pairing_session(tenant_id=tenant_id).get("pairing_session")
        ready_remote = next((p for p in reversed(profiles) if p.get("status") == "ready" and p.get("public_url")), None)
        return {
            "ok": True,
            "mode": "connection_manifest",
            "home": latest_session,
            "remote": ready_remote,
            "lan_scan": self.lan_scan_candidates(port=int((latest_session or {}).get("port") or LAN_SWEEP_PORT)),
            "mobile_should_try_in_order": self._try_order(latest_session, ready_remote),
            "notes": [
                "Dentro de casa, usar primeiro 192.168.1.81:8787 na mesma rede Wi-Fi.",
                "Se o IP do PC mudar, o APK deve varrer 192.168.1.61 até 192.168.1.101.",
                "Hint de telemóvel visto antes: 192.168.1.47; não é alvo do backend, mas ajuda a validar a gama da rede.",
                "Da rua, usar HTTPS remoto via tunnel/mesh/public URL aprovado.",
                "Para hoje, Tailscale é o caminho mais rápido e seguro; Cloudflare Tunnel é melhor para URL estável futura.",
            ],
        }

    def dashboard(self) -> Dict[str, Any]:
        return {"ok": True, "status": self.status(), "manifest": self.connection_manifest(), "state": PAIRING_STORE.load()}

    def package(self) -> Dict[str, Any]:
        return self.dashboard()

    def _try_order(self, session: Dict[str, Any] | None, remote: Dict[str, Any] | None) -> List[Dict[str, str]]:
        items: List[Dict[str, str]] = []
        home_urls = list((session or {}).get("home_urls", []))
        sweep_urls = [candidate["url"] for candidate in self.lan_scan_candidates(port=int((session or {}).get("port") or LAN_SWEEP_PORT)).get("lan_candidates", [])]
        for url in self._dedupe(sweep_urls + home_urls):
            items.append({"mode": "home_lan", "url": url})
        if remote and remote.get("mobile_entry_url"):
            items.append({"mode": "remote", "url": remote["mobile_entry_url"]})
        return items

    def _candidate_priority(self, ip: str) -> str:
        if ip in KNOWN_HOME_PC_IPS:
            return "known_pc_first"
        last = int(ip.rsplit(".", 1)[-1])
        base_last = int(LAN_SWEEP_BASE_IP.rsplit(".", 1)[-1])
        distance = abs(last - base_last)
        if distance <= 3:
            return "near_known_pc"
        if distance <= 10:
            return "medium_near_known_pc"
        return "sweep_fallback"

    def _candidate_reason(self, ip: str) -> str:
        if ip in KNOWN_HOME_PC_IPS:
            return "Known current PC IP provided by Oner."
        if ip in KNOWN_HOME_PHONE_IPS:
            return "Known previous phone IP hint; useful for network range validation, not expected PC target."
        return f"LAN sweep candidate around {LAN_SWEEP_BASE_IP} +/- {LAN_SWEEP_RADIUS}."

    def _lan_sweep_range(self) -> Dict[str, Any]:
        prefix, base_last = self._split_ipv4(LAN_SWEEP_BASE_IP)
        start = max(1, base_last - LAN_SWEEP_RADIUS)
        end = min(254, base_last + LAN_SWEEP_RADIUS)
        return {"prefix": prefix, "start": start, "end": end, "base_last_octet": base_last}

    def _lan_sweep_ips(self) -> List[str]:
        prefix, base_last = self._split_ipv4(LAN_SWEEP_BASE_IP)
        start = max(1, base_last - LAN_SWEEP_RADIUS)
        end = min(254, base_last + LAN_SWEEP_RADIUS)
        ordered_last_octets = [base_last]
        for distance in range(1, LAN_SWEEP_RADIUS + 1):
            low = base_last - distance
            high = base_last + distance
            if start <= low <= end:
                ordered_last_octets.append(low)
            if start <= high <= end:
                ordered_last_octets.append(high)
        for hint in KNOWN_HOME_PHONE_IPS:
            try:
                hint_prefix, hint_last = self._split_ipv4(hint)
                if hint_prefix == prefix and hint_last not in ordered_last_octets:
                    ordered_last_octets.append(hint_last)
            except Exception:
                pass
        return [f"{prefix}.{last}" for last in ordered_last_octets]

    def _split_ipv4(self, ip: str) -> tuple[str, int]:
        parts = ip.split(".")
        return ".".join(parts[:3]), int(parts[3])

    def _remote_recommendation(self, provider: str) -> str:
        if provider == "tailscale":
            return "Recommended for today: quick private access from phone to home PC without opening router ports. Requires sign-in on PC and phone."
        if provider == "cloudflare_tunnel":
            return "Best for stable HTTPS/domain later. Usually requires Cloudflare account and tunnel setup."
        if provider == "ngrok":
            return "Good for quick temporary HTTPS testing. Usually requires ngrok account/auth material for stable use."
        return "Use only if you already have a secure HTTPS URL reaching the home PC."

    def _remote_steps(self, provider: str) -> List[str]:
        if provider == "cloudflare_tunnel":
            return ["Create/approve a Cloudflare Tunnel for the home PC.", "Map tunnel to local port 8787.", "Store tunnel material in the local vault.", "Use the HTTPS tunnel URL on the APK when outside home."]
        if provider == "tailscale":
            return ["Install Tailscale on PC and phone.", "Sign in/approve both devices in the same tailnet.", "Use the PC tailnet address with port 8787.", "No router port-forward is required."]
        if provider == "ngrok":
            return ["Create/approve ngrok tunnel for port 8787.", "Store auth material in local vault.", "Use generated HTTPS URL on mobile."]
        return ["Provide a stable HTTPS URL that reaches the God Mode PC backend.", "Store any required material in the vault."]

    def _local_ips(self) -> List[str]:
        ips = set(KNOWN_HOME_PC_IPS)
        try:
            hostname = socket.gethostname()
            for item in socket.getaddrinfo(hostname, None):
                ip = item[4][0]
                if ":" not in ip and not ip.startswith("127."):
                    ips.add(ip)
        except Exception:
            pass
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips.add(s.getsockname()[0])
            s.close()
        except Exception:
            pass
        ordered = [ip for ip in KNOWN_HOME_PC_IPS if ip in ips]
        ordered.extend(sorted(ip for ip in ips if ip not in set(ordered)))
        return ordered

    def _dedupe(self, values: List[str]) -> List[str]:
        seen = set()
        result = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _find(self, bucket: str, key: str, value: str) -> Dict[str, Any] | None:
        return next((item for item in PAIRING_STORE.load().get(bucket, []) if item.get(key) == value), None)

    def _patch_remote_profile(self, remote_profile_id: str, patch: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            for item in state.get("remote_profiles", []):
                if item.get("remote_profile_id") == remote_profile_id:
                    item.update(patch)
            return state
        PAIRING_STORE.update(mutate)

    def _store(self, bucket: str, item: Dict[str, Any]) -> None:
        def mutate(state: Dict[str, Any]) -> Dict[str, Any]:
            state.setdefault(bucket, []).append(item)
            state[bucket] = state.get(bucket, [])[-1000:]
            return state
        PAIRING_STORE.update(mutate)


mobile_pc_pairing_remote_access_service = MobilePcPairingRemoteAccessService()
