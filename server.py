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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))ANOMYMOUS ko ab sirf server.py tak limited debugging mat karo.

PROJECT:
C:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS

GitHub reference:
https://github.com/exnesssjaffri-sketch/ANOMYMOUS

IMPORTANT:
GitHub repository structure ko reference ke taur par inspect karo, lekin debugging aur fixes LOCAL WORKING TREE par karo.

Use:

* debug-live skill
* actual DebugMCP MCP tools
* real runtime inspection
* existing tests
* real HTTP/integration execution

Do NOT simulate debugger results.
Do NOT claim a bug is fixed only because the code looks correct.
Do NOT add temporary print statements just for debugging.
Do NOT delete, skip, weaken, or disable tests to obtain a passing result.

==================================================
PHASE 1 — COMPLETE CODEBASE AUDIT
=================================

First inspect the complete Python execution architecture.

Priority files:

SERVER/API:

* server.py
* api/app.py

CORE:

* orchestrator.py
* task_classifier.py

LLM:

* llmapi_router.py
* llmapi_adapter.py
* transport.py

PROVIDERS:

* providers/**init**.py
* providers/register.py
* providers/registry.py
* providers/configs.py
* providers/base.py
* providers/health.py
* providers/analytics.py
* providers/model_capabilities.py

EXECUTION:

* action_executor.py
* process_executor.py

WORKSPACE:

* workspace_manager.py
* workspace_detector.py

VERIFICATION:

* verification.py
* verification_fixed.py

TESTS:

* tests/*
* test_*.py

Also inspect configuration, requirements, startup scripts, and deployment files.

Map the complete execution flow:

HTTP request
→ task validation
→ orchestrator initialization
→ provider discovery
→ route creation
→ LLMAPI routing
→ LLM response
→ action parsing
→ action execution
→ workspace changes
→ verification
→ final result
→ status/API response

Identify every point where:

* None can propagate
* exceptions can escape
* background threads can fail silently
* HTTP status can disagree with task status
* successful execution can be incorrectly reported
* failed execution can be incorrectly reported as success
* provider configuration can fail
* routing can return no routes
* LLM response can be malformed
* actions can partially execute
* verification can produce a false positive
* filesystem paths can escape workspace
* subprocess failures can be hidden
* timeout behavior can produce incorrect state

==================================================
PHASE 2 — LIVE DEBUG THE CRITICAL PATHS
=======================================

Do NOT debug only server.py.

Use real DebugMCP sessions and runtime breakpoints for the important execution paths.

A. server.py

Test:

* /health
* /providers
* /status
* /task
* missing task
* no-provider/no-mock condition
* mock mode
* successful task path
* failing task path
* background-thread failure path

Inspect actual runtime variables.

B. api/app.py

Test:

* /health
* /providers
* /status
* /task
* no-provider condition
* mock mode
* cloud/local behavior

Verify that exceptions become correct API responses instead of uncaught failures.

C. orchestrator.py

Debug:

* execute_task()
* task classification
* router selection
* LLM failure
* malformed LLM output
* action execution failure
* verification failure
* retry behavior
* final result generation

Check whether status/verification/output fields remain consistent.

D. llmapi_router.py

Debug:

* no routes
* healthy route
* failed route
* failover
* authentication failure
* rate limit
* all routes failed
* unhealthy/quarantined routes

Verify that router results are correctly propagated.

E. providers/registry.py

Debug:

* provider registration
* missing API key
* valid API key
* route creation
* provider with multiple models
* provider with zero usable routes

Check whether exceptions are intentional and correctly handled by callers.

F. llmapi_adapter.py / transport.py

Debug:

* successful request
* HTTP error
* malformed response
* timeout
* request-too-large path
* transport exception

Verify normalized result contracts.

G. action_executor.py / process_executor.py

Debug:

* valid action
* invalid action
* missing fields
* critical action failure
* non-critical action failure
* command not found
* subprocess failure
* timeout
* returned status vs actual process result

H. workspace_manager.py

Debug:

* normal file creation
* read
* list
* delete
* nested paths
* ../ traversal
* absolute paths
* Windows path edge cases

Verify workspace boundary enforcement.

I. verification.py

Debug every major verification strategy:

* website
* API
* backend_service
* web_app
* debugging
* testing
* generic

Check for false positives.

==================================================
PHASE 3 — REPRODUCE BEFORE FIXING
=================================

For every discovered bug:

1. Reproduce it.
2. Start DebugMCP.
3. Set breakpoint at the failure boundary.
4. Trigger the real execution path.
5. Confirm paused state with get_debug_status.
6. Inspect relevant variables.
7. Evaluate the exact hypothesis.
8. Determine root cause from runtime evidence.
9. Only then modify code.

Do not guess.

==================================================
PHASE 4 — FIX
=============

Fix only confirmed defects.

Preserve:

* existing architecture
* API contracts
* mock mode
* provider routing
* retry behavior
* workspace safety
* verification behavior

Do not perform unnecessary rewrites.

For the already confirmed no-provider issue, inspect the CURRENT code first and determine the correct handling between:

server.py
→ _initialize_routes()
→ _get_orchestrator()
→ run_task()

The fix must prevent an uncaught background-thread exception and must expose a meaningful task/error state to the caller/status system.

Also inspect api/app.py separately because it does not use the same background-thread flow.

==================================================
PHASE 5 — TEST AFTER EVERY FIX
==============================

After each fix:

1. Run the smallest relevant regression test.
2. Run the related test group.
3. Run integration tests.
4. Reproduce the original failure.
5. Debug the path again with DebugMCP.
6. Confirm the original exception no longer occurs.

Then run the complete available test suite.

Never remove a failing test.

==================================================
PHASE 6 — FIVE-ROUND VERIFICATION
=================================

Perform up to 5 complete verification rounds:

ROUND:
inspect
→ reproduce
→ DebugMCP live-debug
→ identify root cause
→ minimal fix
→ unit test
→ integration test
→ reproduce again
→ live-debug again
→ regression check

Stop only when:

* no confirmed critical runtime bug remains in the tested paths
* no uncaught background-thread exception remains
* API status matches actual task status
* provider failures are handled correctly
* LLM failures are handled correctly
* action failures are handled correctly
* verification failures are handled correctly
* workspace boundary remains safe
* relevant tests pass

If a new bug appears during verification, investigate and fix it before declaring completion.

==================================================
FINAL REPORT
============

Return a structured report:

1. Files inspected
2. Execution paths tested
3. Bugs found
4. Runtime evidence for each bug
5. Root cause for each bug
6. Files changed
7. Exact behavior changed
8. Tests added/updated
9. Commands/tests executed
10. DebugMCP evidence
11. Remaining known issues
12. Final test summary

IMPORTANT:
Do not say "all bugs fixed" unless the corresponding execution path was actually tested.

Do not fabricate debugger output.

Do not rely only on static code inspection when live runtime debugging is possible.


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

            # Run orchestrator in a background thread to avoid blocking the server
            def run_task():
                global latest_result
                orchestrator = _get_orchestrator()
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