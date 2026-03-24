import os
from pathlib import Path
from dotenv import load_dotenv

SECRET_ENV_PATH = Path("/etc/secrets/.env")

if SECRET_ENV_PATH.exists():
    load_dotenv(dotenv_path=SECRET_ENV_PATH)
else:
    load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
    OPENAI_KEY = os.getenv("OPENAI_KEY")

settings = Settings()
