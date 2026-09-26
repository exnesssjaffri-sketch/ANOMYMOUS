#!/usr/bin/env python3

import sys
sys.path.insert(0, "C:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS")

from task_classifier import classify_task
from worker_router import select_best_worker, WORKER_CAPABILITIES, detect_workers

# Mock worker registry for testing
WORKER_REGISTRY = {
    "FCC": {"available": True, "command": "fcc", "version": None, "capabilities": ["implementation", "simple coding", "website creation", "bug fixes"]},
    "Claude": {"available": True, "command": "claude", "version": None, "capabilities": ["architecture", "complex reasoning", "debugging", "code review"]},
    "OpenCode": {"available": True, "command": "opencode", "version": None, "capabilities": ["implementation", "frontend", "full-stack", "refactoring"]}
}

# Test classification logic
print("=== Testing Classification Logic ===")
test_tasks = [
    "Build a simple website",
    "Build a React frontend",
    "Create a backend API",
    "Fix a broken import",
    "Debug login error",
    "Build a complex SaaS dashboard"
]

for task in test_tasks:
    classification = classify_task(task)
    print(f"Task: {task}")
    print(f"Classification: {classification}")
    print()

# Test worker selection logic
print("=== Testing Worker Selection Logic ===")
for task in test_tasks:
    classification = classify_task(task)
    try:
        best_worker = select_best_worker(classification)
        print(f"Task: {task}")
        print(f"Best Worker: {best_worker}")
        print(f"Worker Capabilities: {WORKER_CAPABILITIES[best_worker]}")
        print()
    except ValueError as e:
        print(f"Task: {task} - Error: {e}")
        print()