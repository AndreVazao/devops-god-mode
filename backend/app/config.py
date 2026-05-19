import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECRET_ENV_PATH = Path("/etc/secrets/.env")
LOCAL_ENV_PATH = PROJECT_ROOT / ".env"
DEFAULT_DATA_DIR = Path.home() / ".godmode"


def _load_environment() -> None:
    if SECRET_ENV_PATH.exists():
        load_dotenv(dotenv_path=SECRET_ENV_PATH, override=False)

    if LOCAL_ENV_PATH.exists():
        load_dotenv(dotenv_path=LOCAL_ENV_PATH, override=False)


_load_environment()


def _int_from_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if not raw_value:
        return default

    try:
        return int(raw_value)
    except ValueError:
        return default


def _default_data_dir() -> Path:
    raw_value = os.getenv("GODMODE_DATA_DIR")
    base_dir = Path(raw_value).expanduser() if raw_value else DEFAULT_DATA_DIR
    return base_dir.resolve()


def _default_relay_url() -> str:
    explicit_value = os.getenv("RELAY_URL")
    if explicit_value:
        return explicit_value.rstrip("/")

    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url}/api"

    return "https://devops-god-mode.vercel.app/api"


def _relay_candidates() -> list[str]:
    candidates: list[str] = []

    def _add(value: str | None) -> None:
        if not value:
            return
        normalized = value.rstrip("/")
        if normalized and normalized not in candidates:
            candidates.append(normalized)

    app_host = os.getenv("APP_HOST", "127.0.0.1")
    app_port = _int_from_env("APP_PORT", 8000)
    local_api = f"http://{app_host}:{app_port}/api"
    _add(local_api)
    if app_host != "127.0.0.1":
        _add(f"http://127.0.0.1:{app_port}/api")

    tailscale_pc_ip = os.getenv("TAILSCALE_PC_IP", "100.69.225.48").strip()
    if tailscale_pc_ip:
        _add(f"http://{tailscale_pc_ip}:{app_port}/api")

    render_relay_url = os.getenv("RENDER_RELAY_URL", "").strip()
    _add(render_relay_url)

    _add(_default_relay_url())
    return candidates


class Settings:
    DATA_DIR = _default_data_dir()
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "AndreVazao/devops-god-mode")
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    RELAY_URL = _default_relay_url()
    RELAY_CANDIDATES = _relay_candidates()
    RELAY_TOKEN = os.getenv("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")
    TAILSCALE_PC_IP = os.getenv("TAILSCALE_PC_IP", "100.69.225.48")
    TAILSCALE_PHONE_IP = os.getenv("TAILSCALE_PHONE_IP", "100.109.173.115")
    VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
    VERCEL_ORG_ID = os.getenv("VERCEL_ORG_ID")
    VERCEL_PROJECT_ID = os.getenv("VERCEL_PROJECT_ID")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = _int_from_env("APP_PORT", 8000)
    APP_BASE_URL = os.getenv("APP_BASE_URL", f"http://{APP_HOST}:{APP_PORT}")
    APP_HEALTH_URL = os.getenv("APP_HEALTH_URL", f"{APP_BASE_URL}/health")
    SEMANTIC_INDEX_PATH = os.getenv(
        "SEMANTIC_INDEX_PATH",
        str((DATA_DIR / "semantic_index").resolve()),
    )
    REPOS_PATH = os.getenv(
        "REPOS_PATH",
        str((DATA_DIR / "repos").resolve()),
    )


settings = Settings()
