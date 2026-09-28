#!/usr/bin/env python3
"""
Vercel-compatible Flask app for ANOMYMOUS.

This wraps the existing ANOMYMOUS logic for Vercel deployment.
Preserves API contracts:
    GET  /health
    POST /task
    GET  /status
    GET  /providers
    GET  /analytics

IMPORTANT: Local-only capabilities (subprocess execution, unrestricted filesystem access)
are explicitly reported as unavailable in cloud deployment.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, request, jsonify, send_from_directory

from transport import RealHTTPTransport, MockTransport
from orchestrator import Orchestrator
from llmapi_router import LLMAPIRouter, ProviderRoute
from providers.registry import list_providers, create_transport as reg_create_transport, get_config
from providers.analytics import analytics
from config import REAL_TRANSPORT_CONFIG
import providers

# Cloud deployment detection
IS_VERCEL = os.getenv("VERCEL", "0") == "1"
IS_CLOUD = IS_VERCEL or os.getenv("CLOUD_DEPLOYMENT", "0") == "1"

# NEVER use mock transport by default in production
use_mock = os.getenv("ANOMYMOUS_USE_MOCK", "0") == "1"

# Initialize Flask app (disable built-in static route - we have our own)
app = Flask(__name__, static_folder=None)

# Global state (in-memory, ephemeral in serverless)
latest_result = None

# Module-level variables for lazy initialization
_router = None
_orchestrator = None
_routes_initialized = False
_local_capabilities_available = not IS_CLOUD

def _initialize_routes():
    """Initialize provider routes and orchestrator."""
    global _router, _orchestrator, _routes_initialized
    
    if _routes_initialized:
        return
    
    all_routes = []
    for prov_name in list_providers():
        cfg = get_config(prov_name)
        if not cfg:
            continue
        try:
            if use_mock:
                prov_transport = MockTransport({})
            else:
                prov_transport = reg_create_transport(prov_name)
        except Exception:
            continue
        if prov_transport is None:
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
    
    if all_routes:
        _router = LLMAPIRouter(all_routes, max_candidates=5)
        _orchestrator = Orchestrator(provider="auto", model="auto", transport=None, router=_router)
        print("[INFO] Initialized orchestrator with LLMAPI router supporting multiple providers/models")
    else:
        # No eligible routes - orchestrator will report NO_ELIGIBLE_ROUTE
        _orchestrator = Orchestrator(provider="none", model="none", transport=MockTransport({}))
        print("[WARN] No provider routes available - system will report NO_ELIGIBLE_ROUTE")
    
    _routes_initialized = True


def _get_orchestrator():
    """Get or create the orchestrator."""
    if _orchestrator is None:
        _initialize_routes()
    return _orchestrator


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "cloud": IS_CLOUD})


@app.route("/task", methods=["POST"])
def submit_task():
    """Submit a task for execution."""
    global latest_result
    
    data = request.get_json(silent=True) or {}
    task_text = data.get("task")
    
    if not task_text:
        return jsonify({"error": "Missing task"}), 400
    
    # Get orchestrator
    orchestrator = _get_orchestrator()
    
    # In serverless, we execute synchronously (no background threads)
    # The orchestrator handles its own retry logic internally
    latest_result = orchestrator.execute_task(task_text)
    
    return jsonify({"status": "accepted"}), 202


@app.route("/status", methods=["GET"])
def get_status():
    """Get the latest task result."""
    global latest_result
    
    if latest_result:
        return jsonify(latest_result)
    else:
        return jsonify({"status": "no_result"})


@app.route("/providers", methods=["GET"])
def get_providers():
    """Get list of registered providers."""
    provider_list = []
    for p in list_providers():
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
    return jsonify({"providers": provider_list, "count": len(provider_list)})


@app.route("/analytics", methods=["GET"])
def get_analytics():
    """Get analytics summary."""
    summary = analytics.get_summary()
    return jsonify(summary)


@app.route("/capabilities", methods=["GET"])
def get_capabilities():
    """
    Report available capabilities.
    
    Cloud deployment MUST explicitly report local-only capabilities as unavailable.
    """
    return jsonify({
        "local_filesystem": _local_capabilities_available,
        "subprocess_execution": _local_capabilities_available,
        "workspace_operations": _local_capabilities_available,
        "background_tasks": not IS_CLOUD,  # Serverless doesn't support background threads
        "persistent_state": not IS_CLOUD,   # In-memory state is ephemeral in serverless
        "cloud_deployment": IS_CLOUD,
        "note": "Local-only capabilities are unavailable in cloud deployment" if IS_CLOUD else "All capabilities available locally"
    })


# Static file serving (for local development only - Vercel handles static files differently)
@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files from the static/ directory."""
    # Security: prevent directory traversal
    if ".." in filename or filename.startswith("/"):
        return jsonify({"error": "Forbidden"}), 403

    static_dir = (PROJECT_ROOT / "static").resolve()
    file_path = (static_dir / filename).resolve()

    # Check path is within static directory
    if not str(file_path).startswith(str(static_dir)):
        return jsonify({"error": "Forbidden"}), 403

    if not file_path.is_file():
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(str(static_dir), filename)


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# Vercel requires the app to be available at module level
if __name__ == "__main__":
    # For local testing
    app.run(host="127.0.0.1", port=8000, debug=True)