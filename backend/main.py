from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import importlib
import pkgutil
from typing import Any, Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import routes
from app.config import settings
from app.services.relay_worker_service import start_worker
from app.services.semantic_cron import start_semantic_cron

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    start_worker()
    start_semantic_cron()
    yield
    # Shutdown logic (if any)

app = FastAPI(title='DevOps God Mode', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

CANONICAL_HOME_ROUTE = '/app/home'


def _include_all_route_modules() -> List[str]:
    loaded: List[str] = []
    for module_info in sorted(pkgutil.iter_modules(routes.__path__), key=lambda item: item.name):
        module_name = f'{routes.__name__}.{module_info.name}'
        module = importlib.import_module(module_name)
        router = getattr(module, 'router', None)
        if router is not None:
            app.include_router(router)
            loaded.append(module_name)
    return loaded


LOADED_ROUTE_MODULES = _include_all_route_modules()


@app.get('/')
def root() -> Dict[str, str]:
    return {
        'status': 'DevOps God Mode backend alive',
        'home': CANONICAL_HOME_ROUTE,
        'entrypoint_manifest': '/api/app-entrypoint/manifest',
    }


@app.get('/health')
def health() -> Dict[str, str]:
    return {'status': 'ok'}


@app.get('/api/system/config')
def config_status() -> Dict[str, Any]:
    import platform
    import sys

    return {
        'runtime_mode': 'pc_mobile_local_first',
        'local_brain': 'pc',
        'remote_cockpit': 'mobile',
        'canonical_home_route': CANONICAL_HOME_ROUTE,
        'home_visual_shell': CANONICAL_HOME_ROUTE,
        'entrypoint_manifest': '/api/app-entrypoint/manifest',
        'github': bool(settings.GITHUB_TOKEN),
        'openai': bool(settings.OPENAI_KEY),
        'loaded_route_modules': len(LOADED_ROUTE_MODULES),
        'technical_info': {
            'python_version': sys.version,
            'platform': platform.platform(),
            'architecture': platform.machine(),
            'api_modules_loaded': LOADED_ROUTE_MODULES,
        },
    }
