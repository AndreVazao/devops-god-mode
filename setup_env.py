import os
import requests
from pathlib import Path

ENV_PATH = ".env"

DEFAULTS = {
    "RELAY_URL": "",
    "RELAY_TOKEN": "GODMODE_SECURE_TOKEN",
    "GITHUB_TOKEN": "",
    "GITHUB_REPO": "AndreVazao/devops-god-mode",
    "VERCEL_TOKEN": "",
    "VERCEL_PROJECT_ID": "",
    "VERCEL_ORG_ID": "",
    "SEMANTIC_INDEX_PATH": "./semantic_index",
    "REPOS_PATH": "./repos"
}


def ask(key, default=""):
    value = input(f"{key} [{default}]: ").strip()
    return value if value else default


def create_env():
    print("\n=== GOD MODE ENV SETUP ===\n")

    env_data = {}

    for key, default in DEFAULTS.items():
        env_data[key] = ask(key, default)

    with open(ENV_PATH, "w") as f:
        for k, v in env_data.items():
            f.write(f"{k}={v}\n")

    print("\n.env criado com sucesso.\n")

    return env_data


def validate_paths(env):
    print("Validar paths...")

    Path(env["SEMANTIC_INDEX_PATH"]).mkdir(parents=True, exist_ok=True)
    Path(env["REPOS_PATH"]).mkdir(parents=True, exist_ok=True)

    print("✔ Paths OK")


def validate_relay(env):
    print("Validar Relay...")

    if not env["RELAY_URL"]:
        print("⚠ RELAY_URL vazio, a ignorar validação.")
        return

    try:
        r = requests.get(
            f"{env['RELAY_URL']}/health",
            headers={"Authorization": f"Bearer {env['RELAY_TOKEN']}"},
            timeout=5
        )

        if r.status_code == 200:
            print("✔ Relay OK")
        else:
            print(f"⚠ Relay respondeu com status {r.status_code}")

    except Exception as e:
        print(f"❌ Relay falhou: {e}")


def validate_github(env):
    print("Validar GitHub...")

    if not env["GITHUB_TOKEN"]:
        print("⚠ GITHUB_TOKEN vazio")
        return

    try:
        r = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {env['GITHUB_TOKEN']}"}
        )

        if r.status_code == 200:
            user = r.json().get("login")
            print(f"✔ GitHub OK ({user})")
        else:
            print(f"❌ GitHub erro: {r.status_code}")

    except Exception as e:
        print(f"❌ GitHub falhou: {e}")


def summary():
    print("\n=== RESUMO ===")
    print("✔ .env criado")
    print("✔ Paths preparados")
    print("✔ Validações executadas")
    print("\n👉 Reinicia o backend antes de usar.\n")


def main():
    env = create_env()
    validate_paths(env)
    validate_relay(env)
    validate_github(env)
    summary()


if __name__ == "__main__":
    main()
