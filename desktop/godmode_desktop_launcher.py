from __future__ import annotations

import json
import os
import secrets
import socket
import sys
import threading
import time
import traceback
import urllib.request
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APP_NAME = "GodModeDesktop"
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000
BACKEND_LOCAL_URL = f"http://127.0.0.1:{BACKEND_PORT}"
HOME_URL = f"{BACKEND_LOCAL_URL}/app/home"
HEALTH_URL = f"{BACKEND_LOCAL_URL}/health"

DEFAULT_CONFIG = {
    "runtime_mode": "pc_backend_primary_mobile_remote_cockpit",
    "backend_url": BACKEND_LOCAL_URL,
    "backend_host": BACKEND_HOST,
    "backend_port": BACKEND_PORT,
    "shell_url": HOME_URL,
    "mobile_mode": "simple_intuitive",
    "render_role": "not_required_for_local_first_run",
    "pairing_mode": "qr_or_code",
    "autodetect": {
        "desktop_runtime": True,
        "phone_pairing": True,
        "local_lan_ip": True,
        "local_paths": True,
    },
    "autoconfig": {
        "desktop_shortcut": True,
        "autostart": False,
        "zero_touch_defaults": True,
    },
    "first_run_actions": [
        "create_local_config",
        "start_backend_runtime",
        "wait_for_health",
        "prepare_shortcut_payload",
        "prepare_autostart_payload",
        "prepare_pairing_payload",
        "open_local_home",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def appdata_dir() -> Path:
    base = os.environ.get("APPDATA")
    if not base:
        base = str(Path.home() / "AppData" / "Roaming")
    target = Path(base) / APP_NAME
    target.mkdir(parents=True, exist_ok=True)
    return target


def config_path() -> Path:
    return appdata_dir() / "desktop_runtime_config.json"


def state_path() -> Path:
    return appdata_dir() / "desktop_runtime_state.json"


def log_path() -> Path:
    return appdata_dir() / "desktop_runtime.log"


def diagnostic_html_path() -> Path:
    return appdata_dir() / "desktop_backend_diagnostic.html"


def first_run_payload_path() -> Path:
    return appdata_dir() / "desktop_first_run_payload.json"


def shortcut_payload_path() -> Path:
    return appdata_dir() / "desktop_shortcut_payload.json"


def autostart_payload_path() -> Path:
    return appdata_dir() / "desktop_autostart_payload.json"


def pairing_payload_path() -> Path:
    return appdata_dir() / "godmode-mobile-pairing.json"


def write_log(message: str) -> None:
    line = f"[{utc_now()}] {message}\n"
    try:
        with log_path().open("a", encoding="utf-8") as handle:
            handle.write(line)
    except Exception:
        pass


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ensure_default_config() -> dict[str, Any]:
    path = config_path()
    existing = read_json(path)
    merged = DEFAULT_CONFIG | existing
    merged["backend_url"] = BACKEND_LOCAL_URL
    merged["backend_host"] = BACKEND_HOST
    merged["backend_port"] = BACKEND_PORT
    merged["shell_url"] = HOME_URL
    merged["updated_at"] = utc_now()
    if "created_at" not in merged:
        merged["created_at"] = utc_now()
    write_json(path, merged)
    return merged


def local_lan_ip() -> str | None:
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.settimeout(0.2)
        probe.connect(("8.8.8.8", 80))
        ip = probe.getsockname()[0]
        probe.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    return None


def backend_root() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        bundled = base / "backend"
        if bundled.exists():
            return bundled
    return Path(__file__).resolve().parent.parent / "backend"


def configure_backend_import_path() -> Path:
    root = backend_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    os.environ.setdefault("PYTHONPATH", str(root))
    os.chdir(root)
    write_log(f"backend_root={root}")
    return root


def is_backend_healthy(timeout_seconds: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=timeout_seconds) as response:
            return 200 <= response.status < 400
    except Exception:
        return False


def wait_for_backend(max_seconds: int = 25) -> bool:
    started = time.time()
    while time.time() - started <= max_seconds:
        if is_backend_healthy(timeout_seconds=1.0):
            return True
        time.sleep(0.5)
    return False


def start_backend_thread() -> dict[str, Any]:
    if is_backend_healthy():
        return {"ok": True, "status": "already_running", "url": BACKEND_LOCAL_URL}

    try:
        configure_backend_import_path()
        import uvicorn

        def run_server() -> None:
            try:
                write_log("starting uvicorn main:app on 0.0.0.0:8000")
                uvicorn.run(
                    "main:app",
                    host=BACKEND_HOST,
                    port=BACKEND_PORT,
                    log_level="info",
                    access_log=False,
                )
            except Exception:
                write_log("backend thread crashed:\n" + traceback.format_exc())

        thread = threading.Thread(target=run_server, name="GodModeBackendRuntime", daemon=True)
        thread.start()
        healthy = wait_for_backend(max_seconds=25)
        return {
            "ok": healthy,
            "status": "started" if healthy else "start_timeout",
            "url": BACKEND_LOCAL_URL,
            "thread_alive": thread.is_alive(),
        }
    except Exception as exc:
        write_log("failed to start backend:\n" + traceback.format_exc())
        return {
            "ok": False,
            "status": "start_failed",
            "error_type": exc.__class__.__name__,
            "error": str(exc)[:500],
        }


def ensure_first_run_payload(config: dict[str, Any], runtime: dict[str, Any]) -> None:
    payload = {
        "generated_at": utc_now(),
        "runtime_mode": config.get("runtime_mode"),
        "backend_url": config.get("backend_url"),
        "lan_backend_url": lan_backend_url(),
        "shell_url": config.get("shell_url"),
        "health_url": HEALTH_URL,
        "backend_runtime": runtime,
        "first_run_actions": config.get("first_run_actions", []),
    }
    write_json(first_run_payload_path(), payload)


def ensure_shortcut_payload(config: dict[str, Any]) -> None:
    payload = {
        "generated_at": utc_now(),
        "desktop_shortcut": bool(config.get("autoconfig", {}).get("desktop_shortcut", True)),
        "target_shell_url": config.get("shell_url"),
        "suggested_shortcut_name": APP_NAME,
    }
    write_json(shortcut_payload_path(), payload)


def ensure_autostart_payload(config: dict[str, Any]) -> None:
    payload = {
        "generated_at": utc_now(),
        "autostart": bool(config.get("autoconfig", {}).get("autostart", False)),
        "runtime_mode": config.get("runtime_mode"),
        "target_shell_url": config.get("shell_url"),
    }
    write_json(autostart_payload_path(), payload)


def lan_backend_url() -> str | None:
    ip = local_lan_ip()
    if not ip:
        return None
    return f"http://{ip}:{BACKEND_PORT}"


def ensure_pairing_payload(config: dict[str, Any], runtime: dict[str, Any]) -> None:
    pairing_code = secrets.token_hex(4).upper()
    payload = {
        "generated_at": utc_now(),
        "pairing_mode": config.get("pairing_mode", "qr_or_code"),
        "pairing_code": pairing_code,
        "local_backend_url": BACKEND_LOCAL_URL,
        "lan_backend_url": lan_backend_url(),
        "local_shell_url": HOME_URL,
        "health_url": HEALTH_URL,
        "runtime_mode": config.get("runtime_mode"),
        "backend_runtime": runtime,
    }
    write_json(pairing_payload_path(), payload)


def write_state(config: dict[str, Any], runtime: dict[str, Any], opened: bool) -> None:
    payload = {
        "last_launch_at": utc_now(),
        "shell_url": config.get("shell_url"),
        "backend_url": config.get("backend_url"),
        "lan_backend_url": lan_backend_url(),
        "opened_browser": opened,
        "runtime_mode": config.get("runtime_mode"),
        "backend_runtime": runtime,
        "log_path": str(log_path()),
        "diagnostic_html_path": str(diagnostic_html_path()),
    }
    write_json(state_path(), payload)


def write_diagnostic(runtime: dict[str, Any]) -> Path:
    root = backend_root()
    lan_url = lan_backend_url() or "não detetado"
    html = f"""<!doctype html><html lang='pt-PT'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>God Mode Desktop Diagnóstico</title>
<style>body{{font-family:Arial,sans-serif;background:#050816;color:#eef5ff;padding:24px}}.card{{background:#0f172a;border:1px solid #26344f;border-radius:18px;padding:18px;margin:12px 0}}code{{color:#7dd3fc}}pre{{white-space:pre-wrap;background:#081226;padding:12px;border-radius:12px}}</style></head><body>
<div class='card'><h1>God Mode Desktop não conseguiu abrir o backend</h1><p>O EXE tentou arrancar o backend em <code>{BACKEND_LOCAL_URL}</code>.</p></div>
<div class='card'><h2>Estado</h2><pre>{json.dumps(runtime, ensure_ascii=False, indent=2)}</pre></div>
<div class='card'><h2>URLs para testar</h2><p>PC local: <code>{HEALTH_URL}</code></p><p>Telemóvel: <code>{lan_url}</code></p></div>
<div class='card'><h2>Possíveis causas</h2><p>Firewall do Windows, porta 8000 ocupada, antivírus bloqueou o EXE, backend não foi empacotado, ou dependência Python em falta.</p><p>Log: <code>{log_path()}</code></p><p>Backend root: <code>{root}</code></p></div>
</body></html>"""
    path = diagnostic_html_path()
    path.write_text(html, encoding="utf-8")
    return path


def launch_shell(config: dict[str, Any], runtime: dict[str, Any]) -> bool:
    target = config.get("shell_url") or HOME_URL
    if runtime.get("ok") is not True:
        target = write_diagnostic(runtime).as_uri()
    try:
        return webbrowser.open(str(target), new=1)
    except Exception:
        return False


def main() -> int:
    write_log("launcher starting")
    config = ensure_default_config()
    runtime = start_backend_thread()
    ensure_first_run_payload(config, runtime)
    ensure_shortcut_payload(config)
    ensure_autostart_payload(config)
    ensure_pairing_payload(config, runtime)
    opened = launch_shell(config, runtime)
    write_state(config, runtime, opened)
    write_log(f"launcher done runtime={runtime} opened={opened}")
    if runtime.get("ok") is True:
        while True:
            time.sleep(3600)
    return 0 if runtime.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
