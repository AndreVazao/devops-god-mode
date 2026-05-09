import os
from pathlib import Path

from dotenv import load_dotenv

SECRET_ENV_PATH = Path("/etc/secrets/.env")

if SECRET_ENV_PATH.exists():
    load_dotenv(dotenv_path=SECRET_ENV_PATH)
else:
    load_dotenv()


class Settings:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "AndreVazao/devops-god-mode")
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    RELAY_URL = os.getenv("RELAY_URL")
    RELAY_TOKEN = os.getenv("RELAY_TOKEN")
    SEMANTIC_INDEX_PATH = os.getenv("SEMANTIC_INDEX_PATH", "./semantic_index")
    REPOS_PATH = os.getenv("REPOS_PATH", "./repos")


settings = Settings()
