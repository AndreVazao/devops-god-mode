import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

RELAY_TOKEN = os.environ.get("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")
STATE = {
    "tasks": [],
    "responses": [],
}


def _normalized_path(raw_path: str) -> str:
    path = urlparse(raw_path).path.rstrip("/")
    return path or "/"


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

    def _pull_tasks(self) -> None:
        tasks = STATE["tasks"][:]
        STATE["tasks"] = []
        self._send(tasks)

    def _pull_responses(self) -> None:
        responses = STATE["responses"][:]
        STATE["responses"] = []
        self._send(responses)

    def do_OPTIONS(self) -> None:
        self._send({}, 204)

    def do_GET(self) -> None:
        path = _normalized_path(self.path)

        if path in {"/api/health", "/health"}:
            self._send(
                {
                    "status": "ok",
                    "relay": "single-function",
                    "storage": "in-memory",
                }
            )
            return

        if not self._require_auth():
            return

        if path == "/api/pull":
            self._pull_tasks()
            return

        if path == "/api/responses":
            self._pull_responses()
            return

        self._send({"error": "not_found"}, 404)

    def do_POST(self) -> None:
        path = _normalized_path(self.path)

        if path == "/api/health":
            self._send({"status": "ok"})
            return

        if not self._require_auth():
            return

        data = self._read_json()

        if path == "/api/push":
            STATE["tasks"].append(data)
            self._send({"status": "queued"})
            return

        if path == "/api/pull":
            self._pull_tasks()
            return

        if path == "/api/respond":
            STATE["responses"].append(data)
            self._send({"status": "stored"})
            return

        if path == "/api/responses":
            self._pull_responses()
            return

        self._send({"error": "not_found"}, 404)
