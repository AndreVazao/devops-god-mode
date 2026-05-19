import logging
import threading
import time

import requests

from app.config import settings

from .execution_orchestrator import run_task

logger = logging.getLogger(__name__)


def _relay_candidates() -> list[str]:
    candidates = getattr(settings, "RELAY_CANDIDATES", None) or [settings.RELAY_URL]
    unique: list[str] = []
    for item in candidates:
        normalized = (item or "").rstrip("/")
        if normalized and normalized not in unique:
            unique.append(normalized)
    return unique


def process_task(task):
    logger.info(f"[RelayWorker] Processing task: {task.get('id')} - {task.get('action')}")
    try:
        return run_task(task)
    except Exception as exc:
        logger.error(f"[RelayWorker] Task execution error: {exc}")
        return {"error": str(exc)}


def _pull_tasks(relay_url: str, token: str):
    response = requests.get(
        f"{relay_url}/pull",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    return response


def _send_response(relay_url: str, token: str, task, result) -> None:
    requests.post(
        f"{relay_url}/respond",
        json={
            "task": task,
            "result": result,
            "worker": {
                "source": "backend.app.services.relay_worker_service",
                "relay_url": relay_url,
            },
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )


def worker_loop():
    token = settings.RELAY_TOKEN
    relay_candidates = _relay_candidates()

    if not relay_candidates or not token:
        logger.warning("[RelayWorker] Relay candidates or RELAY_TOKEN not configured. Worker disabled.")
        return

    logger.info(f"[RelayWorker] Starting worker loop with candidates: {relay_candidates}")
    active_relay_url = relay_candidates[0]

    while True:
        handled_cycle = False
        try:
            for relay_url in relay_candidates:
                try:
                    response = _pull_tasks(relay_url, token)
                except requests.RequestException as exc:
                    logger.warning(f"[RelayWorker] Pull failed via {relay_url}: {exc}")
                    continue

                if response.status_code == 403:
                    logger.error("[RelayWorker] Unauthorized. Check RELAY_TOKEN.")
                    time.sleep(30)
                    handled_cycle = True
                    break

                if response.status_code != 200:
                    logger.warning(f"[RelayWorker] Pull returned {response.status_code} via {relay_url}")
                    continue

                payload = response.json()
                tasks = payload if isinstance(payload, list) else []
                if not isinstance(payload, list):
                    logger.warning(f"[RelayWorker] Unexpected payload from {relay_url}: {payload}")

                active_relay_url = relay_url
                for task in tasks:
                    result = process_task(task)
                    _send_response(active_relay_url, token, task, result)

                handled_cycle = True
                break

        except Exception as exc:
            logger.error(f"[RelayWorker] Loop error: {exc}")

        if not handled_cycle:
            logger.warning(f"[RelayWorker] No relay candidate available. Last active: {active_relay_url}")
        time.sleep(5)


def start_worker():
    thread = threading.Thread(target=worker_loop, daemon=True, name="RelayWorker")
    thread.start()
    return thread
