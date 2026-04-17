import json
import os
import sys
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
        "zero_touch_defaults": True,
    },
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
    opened = launch_shell(config)
    write_state(config, opened)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
