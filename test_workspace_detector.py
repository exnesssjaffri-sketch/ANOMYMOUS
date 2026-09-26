#!/usr/bin/env python

import os
import sys

# Ensure the workspace_detector module is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workspace_detector import detect_workers, classify_task, select_best_worker, recover_from_failure

# Test Worker Registry
def test_worker_registry():
    print("=== Testing Worker Registry ===")
    registry = detect_workers()
    for worker, info in registry.items():
        print(f"Worker: {worker}, Available: {info['available']}, Version: {info['version']}")
    
    workers = ["FCC", "Claude", "OpenCode"]
    for worker in workers:
        if worker in registry:
            print(f"✓ {worker} detected.")
        else:
            print(f"✗ {worker} not detected.")

# Test Task Classification
def test_task_classification():
    print("\n=== Testing Task Classification ===")
    tasks = [
        "Build a simple website with a button",
        "Fix a bug in the code",
        "Build a complex SaaS dashboard"
    ]
    
    for task in tasks:
        classification = classify_task(task)
        print(f"Task: {task}")
        print(f"Classification: {classification}")
        
        if "simple" in classification:
            print("✓ Correctly classified as simple.")
        elif "complex" in classification:
            print("✓ Correctly classified as complex.")

# Test Worker Selection
def test_worker_selection():
    print("\n=== Testing Worker Selection ===")
    tasks = [
        "Build a simple website with a button",
        "Debug the application"
    ]
    
    for task in tasks:
        classification = classify_task(task)
        best_worker = select_best_worker(classification)
        print(f"Task: {task}")
        print(f"Best Worker: {best_worker}")
        
        if best_worker in detect_workers() and detect_workers()[best_worker]["available"]:
            print("✓ Worker is available.")

# Test Failure Recovery
def test_failure_recovery():
    print("\n=== Testing Failure Recovery ===")
    error_message = "Module \"./Navbar\" not found."
    task_description = "Build a restaurant website"
    
    repair_task = recover_from_failure(error_message, task_description, None)
    print(f"Repair Task: {repair_task}")
    print("✓ Repair task generated successfully.")

if __name__ == "__main__":
    test_worker_registry()
    test_task_classification()
    test_worker_selection()
    test_failure_recovery()
    print("\n=== Tests Completed ===")

if __name__ == "__main__":
    test_worker_registry()
    test_task_classification()
    test_worker_selection()
    test_website_verification()
    test_failure_recovery()
    test_worker_escalation()
    test_multi_worker_mode()
    print("\n=== All Tests Completed ===")