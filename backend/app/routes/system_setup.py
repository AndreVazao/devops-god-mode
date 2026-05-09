import os
import httpx
from pathlib import Path
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/api/system", tags=["system-setup"])

@router.get("/setup-validation")
async def validate_setup():
    results = {
        "paths": {"status": "ok", "details": []},
        "relay": {"status": "pending", "details": ""},
        "github": {"status": "pending", "details": ""},
        "env": {
            "SEMANTIC_INDEX_PATH": settings.SEMANTIC_INDEX_PATH,
            "REPOS_PATH": settings.REPOS_PATH,
            "RELAY_URL": settings.RELAY_URL,
            "GITHUB_TOKEN_CONFIGURED": bool(settings.GITHUB_TOKEN)
        }
    }

    # Validate paths
    try:
        Path(settings.SEMANTIC_INDEX_PATH).mkdir(parents=True, exist_ok=True)
        Path(settings.REPOS_PATH).mkdir(parents=True, exist_ok=True)
        results["paths"]["details"] = f"Paths verified/created: {settings.SEMANTIC_INDEX_PATH}, {settings.REPOS_PATH}"
    except Exception as e:
        results["paths"]["status"] = "error"
        results["paths"]["details"] = str(e)

    async with httpx.AsyncClient() as client:
        # Validate Relay
        if not settings.RELAY_URL:
            results["relay"]["status"] = "missing"
            results["relay"]["details"] = "RELAY_URL not configured"
        else:
            try:
                r = await client.get(
                    f"{settings.RELAY_URL}/health",
                    headers={"Authorization": f"Bearer {settings.RELAY_TOKEN}"},
                    timeout=5
                )
                if r.status_code == 200:
                    results["relay"]["status"] = "ok"
                    results["relay"]["details"] = "Relay responds 200 OK"
                else:
                    results["relay"]["status"] = "error"
                    results["relay"]["details"] = f"Relay status code: {r.status_code}"
            except Exception as e:
                results["relay"]["status"] = "error"
                results["relay"]["details"] = str(e)

        # Validate GitHub
        if not settings.GITHUB_TOKEN:
            results["github"]["status"] = "missing"
            results["github"]["details"] = "GITHUB_TOKEN not configured"
        else:
            try:
                r = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {settings.GITHUB_TOKEN}"},
                    timeout=5
                )
                if r.status_code == 200:
                    user = r.json().get("login")
                    results["github"]["status"] = "ok"
                    results["github"]["details"] = f"GitHub OK (User: {user})"
                else:
                    results["github"]["status"] = "error"
                    results["github"]["details"] = f"GitHub status code: {r.status_code}"
            except Exception as e:
                results["github"]["status"] = "error"
                results["github"]["details"] = str(e)

    return results
