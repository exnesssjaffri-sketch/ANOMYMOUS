#!/usr/bin/env python3
"""Simple HTTP server providing a minimal dashboard for ANOMYMOUS.

Endpoints:
    GET /health            - returns JSON {"status": "ok"}
    POST /task             - JSON {"task": "..."} to submit a task
    GET /status            - returns the latest task result (in-memory)
    GET /providers         - returns list of registered providers
    GET /analytics         - returns analytics summary
    GET /static/<file>     - serves static files (HTML/JS/CSS) for the UI
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from threading import Thread
from transport import MockTransport, RealHTTPTransport
from orchestrator import Orchestrator

# Import providers module for registry access
import providers
from providers.analytics import analytics
from config import REAL_TRANSPORT_CONFIG

# Global state (simple in-memory storage)
latest_result = None

# Use RealHTTPTransport by default for production
# MockTransport is only used in tests or when explicitly configured via env var
if os.getenv("ANOMYMOUS_USE_MOCK", "0") == "1":
mock_transport = MockTransport({
    "Create a simple restaurant website with:": {
        "output": json.dumps({
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "thought": "Creating a restaurant website.",
                            "actions": [
                                {
                                    "type": "create_file",
                                    "path": "restaurant/index.html",
                                    "content": "<html><head><title>Restaurant</title></head><body><h1>Welcome</h1></body></html>",
                                    "critical": True
                                },
                                {
                                    "type": "create_file",
                                    "path": "restaurant/style.css",
                                    "content": "body { color: red; font-family: Arial; }",
                                    "critical": True
                                },
                                {
                                    "type": "create_file",
                                    "path": "restaurant/script.js",
                                    "content": "console.log('Restaurant site loaded!');",
                                    "critical": True
                                }
                            ]
                        })
                    }
                }
            ]
        })
    }
})

if os.getenv("ANOMYMOUS_USE_MOCK", "0") == "1":
    transport = mock_transport
else:
    transport = RealHTTPTransport(
        REAL_TRANSPORT_CONFIG["endpoint"],
        REAL_TRANSPORT_CONFIG["api_key"]
    )

orchestrator = Orchestrator(provider="groq", model="llama-3.1-8b-instant", transport=transport)


class SimpleHandler(BaseHTTPRequestHandler):
    def _set_json(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self._set_json(200)
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        elif path == "/status":
            self._set_json(200)
            self.wfile.write(json.dumps(latest_result or {"status": "no_task_yet"}).encode())
        elif path == "/providers":
            self._set_json(200)
            provider_list = []
            for p in providers.list_providers():
                info = providers.get_provider_info(p)
                if info:
                    provider_list.append({
                        "name": p,
                        "display_name": info["name"],
                        "endpoint": info["endpoint"],
                        "auth_type": info["auth_type"],
                        "requires_auth": info["requires_auth"],
                        "anonymous_access": info["anonymous_access"],
                        "rate_limit_info": info["rate_limit_info"],
                        "model_count": len(info["all_models"]),
                    })
            self.wfile.write(json.dumps({
                "providers": provider_list,
                "count": len(provider_list),
            }).encode())
        elif path == "/analytics":
            self._set_json(200)
            summary = analytics.get_summary()
            self.wfile.write(json.dumps(summary, indent=2).encode())
        elif path.startswith("/static/"):
            # Serve static files from the static/ directory
            filename = path[len("/static/"):]
            # Security: prevent directory traversal
            if ".." in filename or filename.startswith("/"):
                self.send_error(403, "Forbidden")
                return
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
            file_path = os.path.normpath(os.path.join(static_dir, filename))
            if not file_path.startswith(static_dir):
                self.send_error(403, "Forbidden")
                return
            if not os.path.isfile(file_path):
                self.send_error(404, "File not found")
                return
            self.send_response(200)
            # Basic content type detection
            if filename.endswith(".html"):
                self.send_header("Content-Type", "text/html")
            elif filename.endswith(".css"):
                self.send_header("Content-Type", "text/css")
            elif filename.endswith(".js"):
                self.send_header("Content-Type", "application/javascript")
            else:
                self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/task":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            task_text = data.get('task')
            if not task_text:
                self._set_json(400)
                self.wfile.write(json.dumps({"error": "Missing task"}).encode())
                return

            # Run orchestrator in a background thread to avoid blocking the server
            def run_task():
                global latest_result
                latest_result = orchestrator.execute_task(task_text)

            Thread(target=run_task, daemon=True).start()
            self._set_json(202)
            self.wfile.write(json.dumps({"status": "accepted"}).encode())
        else:
            self.send_error(404, "Not found")


def run_server(host='127.0.0.1', port=8000):
    print(f"[INFO] Starting server on {host}:{port}...")
    httpd = HTTPServer((host, port), SimpleHandler)
    print(f"ANOMYMOUS server listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    print("[INFO] Initializing server...")
    run_server()
