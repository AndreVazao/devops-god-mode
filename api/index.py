from http.server import BaseHTTPRequestHandler
import json
import os

RELAY_TOKEN = os.environ.get("RELAY_TOKEN", "GODMODE_SECURE_TOKEN")

memory = {
    "queue": [],
    "responses": []
}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.headers.get("Authorization") != f"Bearer {RELAY_TOKEN}":
            self.send_response(403)
            self.end_headers()
            return

        content_length = self.headers.get("Content-Length")
        if content_length:
            length = int(content_length)
            body = self.rfile.read(length)
            data = json.loads(body)
        else:
            data = {}

        if self.path == "/api/push":
            memory["queue"].append(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"queued"}')

        elif self.path == "/api/pull":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(memory["queue"]).encode())
            memory["queue"] = []

        elif self.path == "/api/respond":
            memory["responses"].append(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"responded"}')

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # Adding a health check or similar if needed, but following instructions mostly
        if self.path == "/api/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            self.send_response(404)
            self.end_headers()
