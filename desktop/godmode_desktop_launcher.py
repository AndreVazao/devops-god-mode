import json
import os
import webbrowser
from pathlib import Path
from datetime import datetime, timezone

APP_NAME = "GodModeDesktop"
DEFAULT_CONFIG = {
    "runtime_mode": "pc_and_phone_primary",
    "backend_url": "http://127.0.0.1:8787",
    "shell_url": "http://127.0.0.1:4173",
    "mobile_mode": "simple_intuitive",
    "render_role": "temporary_test_only",
    "autodetect": {
        "desktop_runtime": True,
        "phone_pairing": True,
        "tunnel_endpoint": True,
        "local_paths": True,
    },
    "autoconfig": {
        "desktop_shortcut": True,
        "autostart": False,
        "zero_touch_defaults": True,
    },
    "first_run_actions": [
        "create_local_config",
        "prepare_shortcut_payload",
        "prepare_autostart_payload",
        "open_local_cockpit",
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


def first_run_payload_path() -> Path:
    return appdata_dir() / "desktop_first_run_payload.json"


def shortcut_payload_path() -> Path:
    return appdata_dir() / "desktop_shortcut_payload.json"


def autostart_payload_path() -> Path:
    return appdata_dir() / "desktop_autostart_payload.json"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def ensure_default_config() -> dict:
    path = config_path()
    existing = read_json(path)
    merged = DEFAULT_CONFIG | existing
    merged["updated_at"] = utc_now()
    if "created_at" not in merged:
        merged["created_at"] = utc_now()
    write_json(path, merged)
    return merged


def ensure_first_run_payload(config: dict) -> None:
    payload = {
        "generated_at": utc_now(),
        "runtime_mode": config.get("runtime_mode"),
        "backend_url": config.get("backend_url"),
        "shell_url": config.get("shell_url"),
        "first_run_actions": config.get("first_run_actions", []),
    }
    write_json(first_run_payload_path(), payload)


def ensure_shortcut_payload(config: dict) -> None:
    payload = {
        "generated_at": utc_now(),
        "desktop_shortcut": bool(config.get("autoconfig", {}).get("desktop_shortcut", True)),
        "target_shell_url": config.get("shell_url"),
        "suggested_shortcut_name": APP_NAME,
    }
    write_json(shortcut_payload_path(), payload)


def ensure_autostart_payload(config: dict) -> None:
    payload = {
        "generated_at": utc_now(),
        "autostart": bool(config.get("autoconfig", {}).get("autostart", False)),
        "runtime_mode": config.get("runtime_mode"),
        "target_shell_url": config.get("shell_url"),
    }
    write_json(autostart_payload_path(), payload)


def write_state(config: dict, opened: bool) -> None:
    payload = {
        "last_launch_at": utc_now(),
        "shell_url": config.get("shell_url"),
        "backend_url": config.get("backend_url"),
        "opened_browser": opened,
        "runtime_mode": config.get("runtime_mode"),
    }
    write_json(state_path(), payload)


def launch_shell(config: dict) -> bool:
    shell_url = (config.get("shell_url") or "").strip()
    if not shell_url:
        return False
    return webbrowser.open(shell_url, new=1)


def main() -> int:
    config = ensure_default_config()
    ensure_first_run_payload(config)
    ensure_shortcut_payload(config)
    ensure_autostart_payload(config)
    opened = launch_shell(config)
    write_state(config, opened)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
