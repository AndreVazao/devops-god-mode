from __future__ import annotations

import importlib
import pkgutil
import logging
import traceback
import sys
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 for stdout/stderr on Windows before logger initialization.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
os.environ.setdefault('PYTHONUTF8', '1')

# Setup structured logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("backend.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

try:
    from app.config import settings

    # Deferred imports to prevent early crashes during module loading
    def get_relay_worker():
        from app.services.relay_worker_service import start_worker
        return start_worker

    def get_semantic_cron():
        from app.services.semantic_cron import start_semantic_cron
        return start_semantic_cron

    def get_evolution_engine():
        from app.evolution.self_evolution_engine import start_evolution_engine
        return start_evolution_engine

    def get_operational_brain():
        from app.brain.operational_loop import start_operational_brain
        return start_operational_brain

except ImportError as e:
    logger.error(f"CRITICAL: Failed to import core modules: {e}")
    # We log but don't exit here to allow /health to potentially work if basic FastAPI is ok
    # however, settings is usually required.

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("--- GOD MODE STARTUP SEQUENCE ---")

    # Start services with error handling so one failure doesn't crash the whole backend
    services = [
        ("Relay Worker", get_relay_worker),
        ("Semantic Cron", get_semantic_cron),
        ("Evolution Engine", get_evolution_engine),
        ("Operational Brain", get_operational_brain)
    ]

    background_threads = []
    for name, getter in services:
        try:
            logger.info(f"Initiating {name}...")
            starter = getter()
            t = starter()
            if t:
                background_threads.append(t)
                logger.info(f"✅ {name} started successfully.")
            else:
                logger.warning(f"⚠️ {name} did not return a thread handle.")
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            logger.error(traceback.format_exc())

    logger.info("--- STARTUP SEQUENCE COMPLETE ---")
    yield
    logger.info("--- SHUTDOWN SEQUENCE STARTING ---")
    logger.info("God Mode services shutting down...")


app = FastAPI(title="DevOps God Mode", lifespan=lifespan)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error caught: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CANONICAL_HOME_ROUTE = "/app/home"


def _include_all_route_modules() -> List[str]:
    loaded: List[str] = []
    try:
        try:
            routes = importlib.import_module("app.routes")
        except Exception:
            logger.warning("Routes package not available; skipping route auto-load.")
            return loaded

        if not hasattr(routes, "__path__"):
            logger.warning("Routes path not found")
            return loaded

        logger.info("Loading route modules...")
        for module_info in sorted(pkgutil.iter_modules(routes.__path__), key=lambda item: item.name):
            module_name = f"{routes.__name__}.{module_info.name}"
            try:
                module = importlib.import_module(module_name)
                router = getattr(module, "router", None)
                if router is not None:
                    app.include_router(router)
                    loaded.append(module_name)
                else:
                    logger.debug(f"Module {module_name} has no router attribute")
            except Exception as e:
                logger.error(f"Failed to load route module {module_name}: {e}")
                continue
    except Exception as e:
        logger.error(f"Critical error loading routes: {e}")

    logger.info(f"Successfully loaded {len(loaded)} route modules.")
    return loaded


LOADED_ROUTE_MODULES = _include_all_route_modules()


@app.get("/")
def root() -> Dict[str, str]:
    try:
        health_url = settings.APP_HEALTH_URL
    except:
        health_url = "/health"

    return {
        "status": "DevOps God Mode backend alive (Resilient Mode)",
        "home": CANONICAL_HOME_ROUTE,
        "health": health_url,
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/system/config")
def config_status() -> Dict[str, Any]:
    import platform
    import sys

    try:
        github = bool(settings.GITHUB_TOKEN)
        openai = bool(settings.OPENAI_KEY)
        relay_url = settings.RELAY_URL
        app_base_url = settings.APP_BASE_URL
        app_health_url = settings.APP_HEALTH_URL
    except:
        github = False
        openai = False
        relay_url = "unknown"
        app_base_url = "unknown"
        app_health_url = "unknown"

    return {
        "runtime_mode": "pc_mobile_local_first",
        "local_brain": "pc",
        "remote_cockpit": "mobile",
        "canonical_home_route": CANONICAL_HOME_ROUTE,
        "github": github,
        "openai": openai,
        "relay_url": relay_url,
        "app_base_url": app_base_url,
        "app_health_url": app_health_url,
        "loaded_route_modules": len(LOADED_ROUTE_MODULES),
        "technical_info": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "api_modules_loaded": LOADED_ROUTE_MODULES,
        },
    }


if __name__ == "__main__":
    import uvicorn
    try:
        host = settings.APP_HOST
        port = settings.APP_PORT
    except:
        host = "0.0.0.0"
        port = 8000

    logger.info(f"Manual start on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
