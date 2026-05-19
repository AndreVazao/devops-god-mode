import json
import os
import time
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

RELAY_TOKEN = os.environ.get("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")
RELAY_PUBLIC_URL = os.environ.get("RELAY_PUBLIC_URL", "https://devops-god-mode.vercel.app").rstrip("/")
LEASE_SECONDS = int(os.environ.get("RELAY_LEASE_SECONDS", "120"))
MAX_BATCH_SIZE = int(os.environ.get("RELAY_MAX_BATCH_SIZE", "50"))
UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL", "").rstrip("/")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")
QUEUE_PREFIX = os.environ.get("RELAY_QUEUE_PREFIX", "godmode:relay")

PROVIDER_CATALOG = [
    {
        "id": "chatgpt",
        "name": "ChatGPT",
        "tier": "web free / capped",
        "note": "generalist and coding",
    },
    {
        "id": "grok",
        "name": "Grok",
        "tier": "web free / capped",
        "note": "live web reasoning",
    },
    {
        "id": "gemini",
        "name": "Gemini",
        "tier": "web free / capped",
        "note": "google ecosystem",
    },
    {
        "id": "claude",
        "name": "Claude",
        "tier": "web free / capped",
        "note": "long-form analysis",
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "tier": "web free / capped",
        "note": "strong coding and cost",
    },
    {
        "id": "perplexity",
        "name": "Perplexity",
        "tier": "web free / capped",
        "note": "research and citation flow",
    },
]

AGENT_CATEGORIES = [
    {
        "category": "Orchestration",
        "agents": [
            {"id": "planner", "name": "Planner", "fn": "define sequence, scope and execution plan"},
            {"id": "dispatcher", "name": "Dispatcher", "fn": "route work to the right worker"},
        ],
    },
    {
        "category": "Coding",
        "agents": [
            {"id": "frontend-agent", "name": "Frontend Agent", "fn": "UI, state, shell and browser flows"},
            {"id": "backend-agent", "name": "Backend Agent", "fn": "APIs, queues, orchestration and persistence"},
            {"id": "integration-agent", "name": "Integration Agent", "fn": "contracts, payloads and connectors"},
        ],
    },
    {
        "category": "Quality",
        "agents": [
            {"id": "qa-agent", "name": "QA Agent", "fn": "smoke tests, regressions and validation"},
            {"id": "review-agent", "name": "Review Agent", "fn": "risk review and diff audit"},
        ],
    },
    {
        "category": "Operations",
        "agents": [
            {"id": "deploy-agent", "name": "Deploy Agent", "fn": "build, publish and rollback checks"},
            {"id": "incident-agent", "name": "Incident Agent", "fn": "runtime triage and recovery"},
        ],
    },
]

DEPLOYERS = [
    {"id": "vercel", "name": "Vercel", "fn": "frontend shell, relay and production web"},
    {"id": "supabase", "name": "Supabase", "fn": "database, auth, functions and storage"},
    {"id": "render", "name": "Render", "fn": "backend services and worker hosting"},
    {"id": "cloudflare", "name": "Cloudflare", "fn": "edge, DNS and tunnel-style exposure"},
    {"id": "github-actions", "name": "GitHub Actions", "fn": "CI, smoke tests and automation workflows"},
]

DEFAULT_REPOS = [
    "AndreVazao/devops-god-mode",
    "AndreVazao/devop-god-mode-jules",
    "AndreVazao/devops-god-mode-mobile",
]

STATE = {
    "tasks": [],
    "inflight": {},
    "responses": [],
}


def _normalized_path(raw_path: str) -> str:
    path = urlparse(raw_path).path.rstrip("/")
    return path or "/"


def _now() -> int:
    return int(time.time())


def _json_dumps(data) -> str:
    return json.dumps(data, separators=(",", ":"), sort_keys=True)


def _chunked_pairs(values):
    return zip(values[::2], values[1::2])


def _canonical_task(task: dict) -> dict:
    normalized = dict(task or {})
    normalized.setdefault("id", f"task-{int(time.time() * 1000)}")
    normalized.setdefault("created_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    normalized.setdefault("source", "unknown")
    return normalized


class InMemoryStore:
    mode = "in-memory-lease"

    def _requeue_stale(self) -> None:
        now = _now()
        stale_ids = [
            task_id
            for task_id, meta in STATE["inflight"].items()
            if meta.get("expires_at", 0) <= now
        ]
        for task_id in stale_ids:
            task = STATE["inflight"].pop(task_id)["task"]
            STATE["tasks"].append(task)

    def push_task(self, task: dict) -> None:
        normalized = _canonical_task(task)
        task_id = normalized["id"]
        queued_ids = {entry["id"] for entry in STATE["tasks"]}
        if task_id in queued_ids or task_id in STATE["inflight"]:
            return
        STATE["tasks"].append(normalized)

    def pull_tasks(self, limit: int):
        self._requeue_stale()
        batch = STATE["tasks"][:limit]
        STATE["tasks"] = STATE["tasks"][limit:]
        expires_at = _now() + LEASE_SECONDS
        for task in batch:
            STATE["inflight"][task["id"]] = {
                "task": task,
                "expires_at": expires_at,
            }
        return batch

    def store_response(self, response: dict) -> None:
        task = response.get("task") or {}
        task_id = task.get("id")
        if task_id:
            STATE["inflight"].pop(task_id, None)
        STATE["responses"].append(response)

    def pull_responses(self, limit: int):
        batch = STATE["responses"][:limit]
        STATE["responses"] = STATE["responses"][limit:]
        return batch

    def health(self) -> dict:
        self._requeue_stale()
        return {
            "queued": len(STATE["tasks"]),
            "inflight": len(STATE["inflight"]),
            "responses": len(STATE["responses"]),
        }


class UpstashStore:
    mode = "upstash-redis"

    def __init__(self) -> None:
        self.tasks_key = f"{QUEUE_PREFIX}:tasks"
        self.inflight_key = f"{QUEUE_PREFIX}:inflight"
        self.responses_key = f"{QUEUE_PREFIX}:responses"

    def _request(self, *segments: str, body: str | None = None):
        encoded_segments = "/".join(quote(str(segment), safe="") for segment in segments)
        url = f"{UPSTASH_URL}/{encoded_segments}"
        data = body.encode("utf-8") if body is not None else None
        request = Request(url, data=data)
        request.add_header("Authorization", f"Bearer {UPSTASH_TOKEN}")
        if body is not None:
            request.add_header("Content-Type", "text/plain; charset=utf-8")

        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"Upstash request failed: {exc}") from exc

        if payload.get("error"):
            raise RuntimeError(payload["error"])
        return payload.get("result")

    def _multi_exec(self, commands):
        request = Request(
            f"{UPSTASH_URL}/multi-exec",
            data=json.dumps(commands).encode("utf-8"),
        )
        request.add_header("Authorization", f"Bearer {UPSTASH_TOKEN}")
        request.add_header("Content-Type", "application/json")

        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"Upstash transaction failed: {exc}") from exc

        for item in payload:
            if item.get("error"):
                raise RuntimeError(item["error"])
        return payload

    def _requeue_stale(self) -> None:
        lease_values = self._request("hgetall", self.inflight_key) or []
        now = _now()
        for task_id, raw_meta in _chunked_pairs(lease_values):
            meta = json.loads(raw_meta)
            if meta.get("expires_at", 0) > now:
                continue
            self._multi_exec(
                [
                    ["LREM", self.inflight_key, "1", meta["raw"]],
                    ["RPUSH", self.tasks_key, meta["raw"]],
                    ["HDEL", self.inflight_key, task_id],
                ]
            )

    def push_task(self, task: dict) -> None:
        normalized = _canonical_task(task)
        self._request("rpush", self.tasks_key, body=_json_dumps(normalized))

    def pull_tasks(self, limit: int):
        self._requeue_stale()
        tasks = []
        expires_at = _now() + LEASE_SECONDS
        for _ in range(limit):
            raw_task = self._request("rpoplpush", self.tasks_key, self.inflight_key)
            if raw_task is None:
                break
            task = json.loads(raw_task)
            task_id = task.get("id")
            if not task_id:
                continue
            lease_meta = _json_dumps({"raw": raw_task, "expires_at": expires_at})
            self._request("hset", self.inflight_key, task_id, body=lease_meta)
            tasks.append(task)
        return tasks

    def store_response(self, response: dict) -> None:
        commands = []
        task = response.get("task") or {}
        task_id = task.get("id")
        if task_id:
            lease_meta = self._request("hget", self.inflight_key, task_id)
            if lease_meta:
                raw_task = json.loads(lease_meta)["raw"]
                commands.extend(
                    [
                        ["LREM", self.inflight_key, "1", raw_task],
                        ["HDEL", self.inflight_key, task_id],
                    ]
                )
        commands.append(["LPUSH", self.responses_key, _json_dumps(response)])
        self._multi_exec(commands)

    def pull_responses(self, limit: int):
        results = []
        for _ in range(limit):
            raw_response = self._request("rpop", self.responses_key)
            if raw_response is None:
                break
            results.append(json.loads(raw_response))
        return results

    def health(self) -> dict:
        self._requeue_stale()
        queued = self._request("llen", self.tasks_key) or 0
        inflight = self._request("hlen", self.inflight_key) or 0
        responses = self._request("llen", self.responses_key) or 0
        return {
            "queued": int(queued),
            "inflight": int(inflight),
            "responses": int(responses),
        }


def _build_store():
    if UPSTASH_URL and UPSTASH_TOKEN:
        try:
            return UpstashStore()
        except Exception:
            pass
    return InMemoryStore()


STORE = _build_store()


def _public_config() -> dict:
    mobile_entry = f"{RELAY_PUBLIC_URL}/app/mobile"
    return {
        "status": "ok",
        "relay": "single-function",
        "mode": "cloud-first",
        "relay_url": f"{RELAY_PUBLIC_URL}/api",
        "mobile_entry": mobile_entry,
        "apk_entry": f"{RELAY_PUBLIC_URL}/app/apk-start",
        "desktop_entry": f"{RELAY_PUBLIC_URL}/app/home",
        "storage": STORE.mode,
        "lease_seconds": LEASE_SECONDS,
        "catalog": {
            "repos": DEFAULT_REPOS,
            "providers": PROVIDER_CATALOG,
            "workers": {
                "agents": AGENT_CATEGORIES,
                "deployers": DEPLOYERS,
            },
        },
    }


class handler(BaseHTTPRequestHandler):
    def _auth(self) -> bool:
        auth_header = self.headers.get("Authorization")
        return auth_header == f"Bearer {RELAY_TOKEN}"

    def _read_json(self) -> dict:
        content_length = self.headers.get("Content-Length")
        if not content_length:
            return {}
        length = int(content_length)
        raw_body = self.rfile.read(length) or b"{}"
        return json.loads(raw_body)

    def _send(self, data, code: int = 200) -> None:
        payload = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _require_auth(self) -> bool:
        if self._auth():
            return True
        self._send({"error": "unauthorized"}, 403)
        return False

    def do_OPTIONS(self) -> None:
        self._send({}, 204)

    def do_GET(self) -> None:
        path = _normalized_path(self.path)

        if path in {"/api/health", "/health"}:
            health = _public_config()
            health.update(STORE.health())
            self._send(health)
            return

        if path in {"/api/config", "/api/app-entrypoint/manifest"}:
            self._send(_public_config())
            return

        if not self._require_auth():
            return

        if path == "/api/pull":
            self._send(STORE.pull_tasks(MAX_BATCH_SIZE))
            return

        if path == "/api/responses":
            self._send(STORE.pull_responses(MAX_BATCH_SIZE))
            return

        self._send({"error": "not_found"}, 404)

    def do_POST(self) -> None:
        path = _normalized_path(self.path)

        if path == "/api/health":
            health = _public_config()
            health.update(STORE.health())
            self._send(health)
            return

        if path in {"/api/config", "/api/app-entrypoint/manifest"}:
            self._send(_public_config())
            return

        if not self._require_auth():
            return

        if path == "/api/pull":
            self._send(STORE.pull_tasks(MAX_BATCH_SIZE))
            return

        if path == "/api/responses":
            self._send(STORE.pull_responses(MAX_BATCH_SIZE))
            return

        data = self._read_json()

        if path == "/api/push":
            STORE.push_task(data)
            self._send({"status": "queued", "storage": STORE.mode})
            return

        if path == "/api/respond":
            STORE.store_response(data)
            self._send({"status": "stored", "storage": STORE.mode})
            return

        self._send({"error": "not_found"}, 404)
