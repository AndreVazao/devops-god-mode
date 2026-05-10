import subprocess
import os
import sys

# Add backend to path to use settings
sys.path.append(os.getcwd())
from backend.app.config import settings

def run():
    print("🚀 Deploying to Vercel")

    if not settings.VERCEL_TOKEN:
        print("❌ Error: VERCEL_TOKEN not found in environment.")
        return

    subprocess.run([
        "npx", "vercel",
        "--prod",
        "--token", settings.VERCEL_TOKEN
    ])

if __name__ == "__main__":
    run()
