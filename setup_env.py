import sys
from pathlib import Path

from backend.app.config import settings

ENV_PATH = Path(".env")


def resolved_defaults() -> dict[str, str]:
    return {
        "RELAY_URL": settings.RELAY_URL,
        "RELAY_TOKEN": settings.RELAY_TOKEN,
        "GITHUB_REPO": settings.GITHUB_REPO,
        "VERCEL_PROJECT_ID": settings.VERCEL_PROJECT_ID or "",
        "VERCEL_ORG_ID": settings.VERCEL_ORG_ID or "",
        "SEMANTIC_INDEX_PATH": settings.SEMANTIC_INDEX_PATH,
        "REPOS_PATH": settings.REPOS_PATH,
        "APP_BASE_URL": settings.APP_BASE_URL,
        "APP_HEALTH_URL": settings.APP_HEALTH_URL,
    }


def ensure_paths(env: dict[str, str]) -> None:
    Path(env["SEMANTIC_INDEX_PATH"]).mkdir(parents=True, exist_ok=True)
    Path(env["REPOS_PATH"]).mkdir(parents=True, exist_ok=True)


def write_env_file(env: dict[str, str], overwrite: bool = False) -> Path:
    if ENV_PATH.exists() and not overwrite:
        raise FileExistsError(".env already exists. Use --force to overwrite it.")

    ENV_PATH.write_text(
        "\n".join(f"{key}={value}" for key, value in env.items()) + "\n",
        encoding="utf-8",
    )
    return ENV_PATH


def summary(env: dict[str, str], wrote_file: bool) -> None:
    print("\n=== GOD MODE RUNTIME DEFAULTS ===")
    for key, value in env.items():
        print(f"{key}={value}")

    if wrote_file:
        print(f"\n.env written to {ENV_PATH.resolve()}")
    else:
        print("\nNo .env file is required. Run with --write only if you want an export.")


def main(write: bool = False, overwrite: bool = False) -> None:
    env = resolved_defaults()
    ensure_paths(env)

    wrote_file = False
    if write:
        write_env_file(env, overwrite=overwrite)
        wrote_file = True

    summary(env, wrote_file=wrote_file)


if __name__ == "__main__":
    main(write="--write" in sys.argv, overwrite="--force" in sys.argv)
