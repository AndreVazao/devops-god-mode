import json
import os
from http.server import BaseHTTPRequestHandler

RELAY_TOKEN = os.environ.get("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")

STATE = {
    "tasks": [],
    "responses": []
}

class handler(BaseHTTPRequestHandler):

    def _auth(self):
        auth_header = self.headers.get("Authorization")
        return auth_header == f"Bearer {RELAY_TOKEN}"

    def _read(self):
        content_length = self.headers.get("Content-Length")
        if content_length:
            length = int(content_length)
            return json.loads(self.rfile.read(length) or "{}")
        return {}

    def _send(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        if not self._auth():
            return self._send({"error": "unauthorized"}, 403)

        data = self._read()

        if self.path == "/api/push":
            STATE["tasks"].append(data)
            return self._send({"status": "queued"})

        elif self.path == "/api/pull":
            tasks = STATE["tasks"][:]
            STATE["tasks"] = []
            return self._send(tasks)

        elif self.path == "/api/respond":
            STATE["responses"].append(data)
            return self._send({"status": "stored"})

        elif self.path == "/api/responses":
            res = STATE["responses"][:]
            STATE["responses"] = []
            return self._send(res)

        return self._send({"error": "not_found"}, 404)

    def do_GET(self):
        if self.path == "/api/health":
            return self._send({"status": "ok"})
        return self._send({"error": "not_found"}, 404)
