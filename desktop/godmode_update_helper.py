from __future__ import annotations

import json
import os
import shutil
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

APP_NAME = "GodModeDesktop"
EXE_NAME = "GodModeDesktop.exe"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def appdata_dir() -> Path:
    base = os.environ.get("APPDATA")
    if not base:
        base = str(Path.home() / "AppData" / "Roaming")
    target = Path(base) / APP_NAME
    target.mkdir(parents=True, exist_ok=True)
    return target


def pending_update_path() -> Path:
    return appdata_dir() / "desktop_pending_update.json"


def update_log_path() -> Path:
    return appdata_dir() / "desktop_update.log"


def backup_dir() -> Path:
    target = appdata_dir() / "update_backups"
    target.mkdir(parents=True, exist_ok=True)
    return target


def log(message: str) -> None:
    with update_log_path().open("a", encoding="utf-8") as handle:
        handle.write(f"[{utc_now()}] {message}\n")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def executable_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def find_new_exe(extracted_dir: Path) -> Path | None:
    candidates = list(extracted_dir.rglob(EXE_NAME))
    if not candidates:
        return None
    candidates.sort(key=lambda path: len(str(path)))
    return candidates[0]


def apply_update(package_path: Path, install_dir: Path) -> dict:
    if not package_path.exists():
        return {"ok": False, "error_type": "package_not_found", "package_path": str(package_path)}
    if package_path.suffix.lower() != ".zip":
        return {"ok": False, "error_type": "unsupported_package_type", "package_path": str(package_path)}

    staging = appdata_dir() / "update_staging" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    staging.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package_path, "r") as archive:
        archive.extractall(staging)

    new_exe = find_new_exe(staging)
    if not new_exe:
        return {"ok": False, "error_type": "new_exe_not_found_in_package", "staging": str(staging)}

    current_exe = install_dir / EXE_NAME
    backup_target = backup_dir() / f"{EXE_NAME}.{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.bak"
    if current_exe.exists():
        shutil.copy2(current_exe, backup_target)

    target_tmp = install_dir / f"{EXE_NAME}.new"
    shutil.copy2(new_exe, target_tmp)

    replaced = False
    last_error = None
    for _ in range(20):
        try:
            if current_exe.exists():
                current_exe.unlink()
            target_tmp.rename(current_exe)
            replaced = True
            break
        except Exception as exc:
            last_error = str(exc)
            time.sleep(0.5)

    if not replaced:
        if backup_target.exists() and not current_exe.exists():
            shutil.copy2(backup_target, current_exe)
        return {
            "ok": False,
            "error_type": "replace_failed",
            "error": last_error,
            "backup": str(backup_target),
        }

    return {
        "ok": True,
        "status": "updated",
        "installed_exe": str(current_exe),
        "backup": str(backup_target) if backup_target.exists() else None,
        "staging": str(staging),
    }


def main() -> int:
    log("update helper started")
    pending = read_json(pending_update_path())
    package = pending.get("package_path") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not package:
        result = {"ok": False, "error_type": "missing_package_path"}
        write_json(appdata_dir() / "desktop_update_last_result.json", result)
        log(json.dumps(result, ensure_ascii=False))
        return 2

    install_dir = executable_dir()
    result = apply_update(Path(package).expanduser(), install_dir)
    result["finished_at"] = utc_now()
    result["install_dir"] = str(install_dir)
    write_json(appdata_dir() / "desktop_update_last_result.json", result)
    if result.get("ok"):
        try:
            pending_update_path().unlink(missing_ok=True)
        except Exception:
            pass
    log(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
