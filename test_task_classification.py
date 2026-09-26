#!/usr/bin/env python3

import sys
sys.path.insert(0, os.path.abspath("c:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS"))

from task_classifier import classify_task
from worker_registry import detect_workers
from worker_router import select_best_worker

# Test A: Simple Task Classification
print("=== Test A: Simple Task Classification ===")
task_description = "Build a simple website"
task_classification = classify_task(task_description)
print(f"Task Classification: {task_classification}")

# Detect workers
print("\nWorker Registry:")
detect_workers()
for worker, info in detect_workers().items():
    print(f"{worker}: Available = {info['available']}")

# Select best worker
try:
    best_worker = select_best_worker(task_classification)
    print(f"Best Worker: {best_worker}")
except ValueError as e:
    print(f"Error: {e}")

# Test B: Debugging Task Classification
print("\n=== Test B: Debugging Task Classification ===")
task_description = "Fix a broken import"
task_classification = classify_task(task_description)
print(f"Task Classification: {task_classification}")

# Select best worker
try:
    best_worker = select_best_worker(task_classification)
    print(f"Best Worker: {best_worker}")
except ValueError as e:
    print(f"Error: {e}")

# Test C: No FCC Available
print("\n=== Test C: No FCC Available ===")
# Simulate FCC as unavailable
from worker_registry import WORKER_REGISTRY
WORKER_REGISTRY["FCC"]["available"] = False
detect_workers()

try:
    task_description = "Build a complex SaaS dashboard"
    task_classification = classify_task(task_description)
    best_worker = select_best_worker(task_classification)
    print(f"Best Worker: {best_worker}")
except ValueError as e:
    print(f"Error: {e}")