#!/usr/bin/env python3
"""Simple HTTP server providing a minimal dashboard for ANOMYMOUS.

This server uses the LLMAPI router for dynamic provider/model selection
instead of hardcoded Groq/llama-3.1-8b-instant.

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
import providers
from providers.analytics import analytics
from config import REAL_TRANSPORT_CONFIG

# Global state (simple in-memory storage)
latest_result = None

# Initialize transport (MockTransport only for tests when explicitly enabled)
if os.getenv("ANOMYMOUS_USE_MOCK", "0") == "1":
    transport = MockTransport({
        "Create a simple restaurant website:": {
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
else:
    transport = RealHTTPTransport(
        REAL_TRANSPORT_CONFIG["endpoint"],
        REAL_TRANSPORT_CONFIG["api_key"]
    )
# Build multi-provider routes from the registry using LLMAPI router
# This replaces hardcoded provider/model with dynamic selection
# The router provides dynamic provider/model selection and failover
from llmapi_router import LLMAPIRouter, ProviderRoute
from providers.registry import list_providers, create_transport as reg_create_transport, get_config

all_routes = []
for prov_name in list_providers():
    cfg = get_config(prov_name)
    if not cfg:
        continue
    try:
        prov_transport = reg_create_transport(prov_name)
    except Exception:
        continue
    models_to_use = cfg.default_models[:3] if cfg.default_models else cfg.all_models[:3]
    for model_info in models_to_use:
        route = ProviderRoute(
            provider=prov_name,
            model=model_info.id,
            transport=prov_transport,
            max_tokens=model_info.context_window,
            priority=1,
            weight=1.0,
        )
        all_routes.append(route)

# Use router for dynamic provider/model selection
# If no routes found (e.g., no API keys), fall back to simple transport
if all_routes:
    router = LLMAPIRouter(all_routes, max_candidates=5)
    orchestrator = Orchestrator(provider="auto", model="auto", transport=None, router=router)
    print("[INFO] Initialized orchestrator with LLMAPI router supporting multiple providers/models")
else:
    orchestrator = Orchestrator(provider="groq", model="llama-3.1-8b-instant", transport=transport)
    print("[WARN] No provider routes available, using fallback configuration")


class SimpleHandler(BaseHTTPRequestHandler):
    def _set_json(self, status_code):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._set_json(200)
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        elif parsed.path == "/status":
            self._set_json(200)
            global latest_result
            if latest_result:
                self.wfile.write(json.dumps(latest_result).encode())
            else:
                self.wfile.write(json.dumps({"status": "no_result"}).encode())
        elif parsed.path == "/providers":
            self._set_json(200)
            provider_list = []
            for p, info in providers.list_providers().items():
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
        elif parsed.path == "/analytics":
            self._set_json(200)
            summary = analytics.get_summary()
            self.wfile.write(json.dumps(summary, indent=2).encode())
        elif parsed.path.startswith("/static/"):
            # Serve static files from the static/ directory
            filename = parsed.path[len("/static/"):]
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