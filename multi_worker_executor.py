#!/usr/bin/env python3

import os
import sys

# Import necessary modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worker_registry import WORKER_REGISTRY
from task_classifier import classify_task
from worker_router import select_best_worker, escalate_worker
from verification import verify_website

# Multi-worker mode logic
def multi_worker_mode(task_classification, output_dir):
    workers_used = []
    current_worker = select_best_worker(task_classification)
    workers_used.append(current_worker)
    
    # Simulate worker execution and verification
    verification_results = verify_website(output_dir)
    
    if not all(verification_results.values()):
        # Escalate to another worker if verification fails
        try:
            next_worker = escalate_worker(task_classification, current_worker)
            workers_used.append(next_worker)
            verification_results = verify_website(output_dir)
        except ValueError as e:
            raise e
    
    return workers_used, verification_results

if __name__ == "__main__":
    # Example usage for multi-worker mode
    task_description = "Build a complex SaaS dashboard"
    task_classification = classify_task(task_description)
    output_dir = os.path.join(os.getcwd(), "mock_output")
    
    # Create mock output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create mock files
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write("<html><body><h1>SaaS Dashboard</h1></body></html>")
    
    try:
        workers_used, verification_results = multi_worker_mode(task_classification, output_dir)
        print(f"Workers Used: {workers_used}")
        print(f"Verification Results: {verification_results}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Cleanup
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    os.rmdir(output_dir)