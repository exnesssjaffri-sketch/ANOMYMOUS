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
    GET /capabilities      - returns available capabilities
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
from llmapi_router import LLMAPIRouter
from providers.analytics import analytics
from providers.registry import create_routes, list_providers, get_config
import providers
from config import REAL_TRANSPORT_CONFIG

# Global state (simple in-memory storage)
latest_result = None

# Check if mock mode is enabled
use_mock = os.getenv("ANOMYMOUS_USE_MOCK", "0") == "1"

# Module-level variables for lazy initialization
_router = None
_orchestrator = None
_routes_initialized = False

def _initialize_routes():
    """Initialize provider routes and orchestrator lazily."""
    global _router, _orchestrator, _routes_initialized
    
    if _routes_initialized:
        return
    
    all_routes = []
    for prov_name in list_providers():
        cfg = get_config(prov_name)
        if not cfg:
            continue
        if use_mock:
            # In mock mode, create a mock transport and use it for all routes
            mock_transport = MockTransport({})
            routes = create_routes(prov_name, transport=mock_transport, max_candidates=3)
        else:
            # Production mode - create routes with real transports
            # create_routes handles missing API keys gracefully (skips providers)
            routes = create_routes(prov_name, transport=None, max_candidates=3)
        all_routes.extend(routes)
    
    if all_routes:
        _router = LLMAPIRouter(all_routes, max_candidates=5)
        _orchestrator = Orchestrator(provider="auto", model="auto", transport=None, router=_router)
        print("[INFO] Initialized orchestrator with LLMAPI router supporting multiple providers/models")
    else:
        # No routes available - orchestrator will be None, handled gracefully in handlers
        _orchestrator = None
        print("[WARN] No provider routes available. Set ANOMYMOUS_USE_MOCK=1 for testing or configure API keys.")
    
    _routes_initialized = True


def _get_orchestrator():
    """Get the orchestrator, initializing routes if needed."""
    if not _routes_initialized:
        _initialize_routes()
    return _orchestrator


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
            for p in providers.list_providers():
                info = providers.get_provider_info(p)
                if not info:
                    continue
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

            # Check if orchestrator is available
            orchestrator = _get_orchestrator()
            if orchestrator is None:
                self._set_json(503)
                self.wfile.write(json.dumps({
                    "error": "No orchestrator available. Set ANOMYMOUS_USE_MOCK=1 for testing or configure API keys."
                }).encode())
                return

            # Run orchestrator in a background thread to avoid blocking the server
            def run_task():
                global latest_result
                try:
                    latest_result = orchestrator.execute_task(task_text)
                except Exception as e:
                    latest_result = {
                        "status": "failed",
                        "execution": str(e),
                        "error": str(e)
                    }

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