#!/usr/bin/env python3

import subprocess
from typing import Dict, Any

# Worker registry structure
WORKER_REGISTRY = {
    "FCC": {
        "available": False,
        "command": "fcc",
        "version": None,
    },
    "Claude": {
        "available": False,
        "command": "claude",
        "version": None,
    },
    "OpenCode": {
        "available": False,
        "command": "opencode",
        "version": None,
    }
}

# Mock capabilities for testing
WORKER_CAPABILITIES = {
    "FCC": ["simple", "implementation", "website creation", "bug fixes"],
    "Claude": ["architecture", "complex reasoning", "debugging", "code review"],
    "OpenCode": ["frontend", "full_stack", "implementation", "refactoring"],
}

def is_worker_available(command: str) -> bool:
    try:
        subprocess.run([command, "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def detect_workers() -> Dict[str, Any]:
    global WORKER_REGISTRY
    for worker_name, worker_info in WORKER_REGISTRY.items():
        worker_info["available"] = is_worker_available(worker_info["command"])
        if worker_info["available"]:
            try:
                version_output = subprocess.run(
                    [worker_info["command"], "--version"],
                    capture_output=True,
                    text=True
                )
                worker_info["version"] = version_output.stdout.strip()
            except subprocess.CalledProcessError:
                worker_info["version"] = None
    return WORKER_REGISTRY