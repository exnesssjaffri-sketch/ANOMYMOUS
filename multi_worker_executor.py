#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Import necessary modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_classifier import classify_task
from worker_router import select_best_worker, escalate_worker
from failure_recovery import recover_from_failure
from verification import verify_website

# Multi-worker execution logic
def execute_worker_task(task_classification: Dict[str, bool], output_dir: str) -> Dict[str, Any]:
    """Execute a task using a worker and verify the result."""
    current_worker = select_best_worker(task_classification)
    
    # Simulate worker execution (in a real scenario, this would run actual worker commands)
    # For now, we'll just create a mock output directory and verify
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create mock files based on task classification
    if task_classification.get("frontend", False):
        with open(output_path / "index.html", "w") as f:
            f.write("<html><body><h1>Frontend Task</h1></body></html>")
        with open(output_path / "style.css", "w") as f:
            f.write("body { background: white; }")
        with open(output_path / "script.js", "w") as f:
            f.write("function hello() { console.log('Hello World!'); }")
    
    # Verify the result
    verification_results = verify_website(str(output_path))
    
    if not all(verification_results.values()):
        # Generate a repair task if verification fails
        error_message = "Verification failed. Check the output directory."
        recovery_info = recover_from_failure(error_message, "Build a website", output_dir)
        return {
            "worker": current_worker,
            "status": "failed_verification",
            "recovery_info": recovery_info,
            "verification_results": verification_results
        }
    
    return {
        "worker": current_worker,
        "status": "success",
        "verification_results": verification_results
    }

def multi_worker_execute(task_classification: Dict[str, bool], output_dir: str) -> Dict[str, Any]:
    """Execute a task using multiple workers if needed."""
    workers_used = []
    current_status = None
    
    # Start with the best worker
    current_status = execute_worker_task(task_classification, output_dir)
    workers_used.append(current_status["worker"])
    
    # If verification fails, escalate to another worker
    if current_status.get("status") == "failed_verification":
        try:
            next_worker = escalate_worker(task_classification, current_status["worker"])
            workers_used.append(next_worker)
            current_status = execute_worker_task(task_classification, output_dir)
        except ValueError as e:
            return {
                "error": str(e),
                "workers_used": workers_used
            }
    
    return {
        "workers_used": workers_used,
        "final_status": current_status.get("status", "unknown"),
        "verification_results": current_status.get("verification_results", {})
    }

if __name__ == "__main__":
    # Example usage for multi-worker execution
    task_description = "Build a complex SaaS dashboard"
    task_classification = classify_task(task_description)
    output_dir = str(Path.cwd() / "mock_output")
    
    try:
        result = multi_worker_execute(task_classification, output_dir)
        print(f"Workers Used: {result['workers_used']}")
        print(f"Final Status: {result['final_status']}")
        print(f"Verification Results: {result['verification_results']}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Cleanup
    for file in Path(output_dir).iterdir():
        file.unlink()
    Path(output_dir).rmdir()