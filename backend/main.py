from __future__ import annotations

import importlib
import pkgutil
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import routes
from app.config import settings

app = FastAPI(title='DevOps God Mode')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


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
    return {'status': 'DevOps God Mode backend alive'}


@app.get('/health')
def health() -> Dict[str, str]:
    return {'status': 'ok'}


@app.get('/api/system/config')
def config_status() -> Dict[str, Any]:
    return {
        'runtime_mode': 'pc_mobile_local_first',
        'local_brain': 'pc',
        'remote_cockpit': 'mobile',
        'github': bool(settings.GITHUB_TOKEN),
        'openai': bool(settings.OPENAI_KEY),
        'loaded_route_modules': len(LOADED_ROUTE_MODULES),
    }
