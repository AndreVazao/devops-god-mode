import requests
import time
import os
import threading
import logging
from app.config import settings
from .execution_orchestrator import run_task

logger = logging.getLogger(__name__)

def process_task(task):
    logger.info(f"[RelayWorker] Processing task: {task.get('id')} - {task.get('action')}")
    try:
        return run_task(task)
    except Exception as e:
        logger.error(f"[RelayWorker] Task execution error: {e}")
        return {"error": str(e)}

def worker_loop():
    relay_url = settings.RELAY_URL
    token = settings.RELAY_TOKEN

    if not relay_url or not token:
        logger.warning("[RelayWorker] RELAY_URL or RELAY_TOKEN not configured. Worker disabled.")
        return

    logger.info(f"[RelayWorker] Starting worker loop connecting to {relay_url}")

    while True:
        try:
            # We use POST /pull based on the original code, but relay.js seems to use GET /relay or POST /relay
            # Wait, the original relay_worker_service.py used POST /pull
            # But api/relay.js has:
            # if (method === "GET") { tasks = await kv.lrange(TASKS_KEY, 0, -1); ... }
            # and POST for pushing tasks.
            # And backend/relay_worker.py (the standalone one) uses GET /relay.

            # Let's align with the actual cloud relay implementation in api/relay.js
            # Actually, looking at relay.js:
            # GET returns items from TASKS_KEY.

            r = requests.get(
                f"{relay_url}/relay",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            if r.status_code == 200:
                data = r.json()
                tasks = data.get("items", [])
                for t in tasks:
                    result = process_task(t)

                    # Respond back to state
                    requests.post(
                        f"{relay_url}/state",
                        json={
                            "type": "MESSAGE",
                            "payload": {
                                "chatId": t.get("chat_id") or t.get("chatId") or "default",
                                "message": {
                                    "role": "gm",
                                    "text": str(result.get("message") or result),
                                    "type": "text"
                                }
                            }
                        },
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )
            elif r.status_code == 401:
                logger.error("[RelayWorker] Unauthorized. Check RELAY_TOKEN.")
                time.sleep(30)
            else:
                if r.status_code != 404:
                    logger.debug(f"[RelayWorker] Status code: {r.status_code}")

        except Exception as e:
            logger.error(f"[RelayWorker] Loop error: {e}")

        time.sleep(5)

def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True, name="RelayWorker")
    t.start()
    return t
