from __future__ import annotations

import importlib
import pkgutil
import logging
import traceback
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import routes
from app.config import settings
from app.services.relay_worker_service import start_worker
from app.services.semantic_cron import start_semantic_cron
from app.evolution.self_evolution_engine import start_evolution_engine
from app.brain.operational_loop import start_operational_brain

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("backend.log")
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting God Mode services...")

    # Start services with error handling so one failure doesn't crash the whole backend
    services = [
        ("Relay Worker", start_worker),
        ("Semantic Cron", start_semantic_cron),
        ("Evolution Engine", start_evolution_engine),
        ("Operational Brain", start_operational_brain)
    ]

    background_threads = []
    for name, starter in services:
        try:
            logger.info(f"Starting {name}...")
            t = starter()
            if t:
                background_threads.append(t)
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            logger.error(traceback.format_exc())

    yield
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
    if not hasattr(routes, "__path__"):
        logger.warning("Routes path not found")
        return loaded

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
            # We don't want to crash the whole app if one route fails to load
            continue

    return loaded


LOADED_ROUTE_MODULES = _include_all_route_modules()


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "status": "DevOps God Mode backend alive",
        "home": CANONICAL_HOME_ROUTE,
        "entrypoint_manifest": "/api/app-entrypoint/manifest",
        "health": settings.APP_HEALTH_URL,
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/system/config")
def config_status() -> Dict[str, Any]:
    import platform
    import sys

    return {
        "runtime_mode": "pc_mobile_local_first",
        "local_brain": "pc",
        "remote_cockpit": "mobile",
        "canonical_home_route": CANONICAL_HOME_ROUTE,
        "home_visual_shell": CANONICAL_HOME_ROUTE,
        "entrypoint_manifest": "/api/app-entrypoint/manifest",
        "github": bool(settings.GITHUB_TOKEN),
        "openai": bool(settings.OPENAI_KEY),
        "relay_url": settings.RELAY_URL,
        "app_base_url": settings.APP_BASE_URL,
        "app_health_url": settings.APP_HEALTH_URL,
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
    # Respect environment variables for host and port
    host = settings.APP_HOST
    port = settings.APP_PORT
    logger.info(f"Manual start on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
