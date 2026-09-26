#!/usr/bin/env python3

import os
import subprocess

# Worker registry structure
WORKER_REGISTRY = {
    "FCC": {
        "available": False,
        "command": "fcc",
        "version": None,
        "capabilities": ["implementation", "simple coding", "website creation", "bug fixes"],
    },
    "Claude": {
        "available": False,
        "command": "claude",
        "version": None,
        "capabilities": ["architecture", "complex reasoning", "debugging", "code review"],
    },
    "OpenCode": {
        "available": False,
        "command": "opencode",
        "version": None,
        "capabilities": ["implementation", "frontend", "full-stack", "refactoring"],
    }
}

# Detect if a worker is available by checking its command
def is_worker_available(command):
    try:
        subprocess.run([command, "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Detect worker availability and update registry
def detect_workers():
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

if __name__ == "__main__":
    detect_workers()
    print("Worker Registry:")
    for worker, info in WORKER_REGISTRY.items():
        print(f"{worker}: Available = {info['available']}, Command = {info['command']}, Version = {info['version']}")