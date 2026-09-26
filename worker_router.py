#!/usr/bin/env python3

import sys

# Import worker registry
sys.path.insert(0, os.path.abspath("c:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS"))
from worker_registry import detect_workers, WORKER_REGISTRY

# Import task classifier
from task_classifier import classify_task

# Worker capabilities
WORKER_CAPABILITIES = {
    "FCC": ["implementation", "simple coding", "website creation", "bug fixes"],
    "Claude": ["architecture", "complex reasoning", "debugging", "code review"],
    "OpenCode": ["implementation", "frontend", "full-stack", "refactoring"],
}

def select_best_worker(task_classification):
    available_workers = [worker for worker in WORKER_REGISTRY if WORKER_REGISTRY[worker]["available"]]
    if not available_workers:
        raise ValueError("No available workers.")
    
    # Select the worker with the least overlap in capabilities
    best_worker = None
    min_overlap = float('inf')
    
    for worker in available_workers:
        worker_capabilities = WORKER_CAPABILITIES[worker]
        overlap = sum(1 for capability in task_classification if capability in worker_capabilities)
        
        if overlap < min_overlap:
            min_overlap = overlap
            best_worker = worker
    
    return best_worker

def escalate_worker(task_classification, current_worker):
    available_workers = [worker for worker in WORKER_REGISTRY if WORKER_REGISTRY[worker]["available"] and worker != current_worker]
    if not available_workers:
        raise ValueError("No available workers left for escalation.")
    
    # Select the next best worker
    best_worker = None
    min_overlap = float('inf')
    
    for worker in available_workers:
        worker_capabilities = WORKER_CAPABILITIES[worker]
        overlap = sum(1 for capability in task_classification if capability in worker_capabilities)
        
        if overlap < min_overlap:
            min_overlap = overlap
            best_worker = worker
    
    return best_worker

if __name__ == "__main__":
    # Example task classification
    task_description = "Build a simple website"
    task_classification = classify_task(task_description)
    print(f"Task Classification: {task_classification}")
    
    try:
        best_worker = select_best_worker(task_classification)
        print(f"Best Worker: {best_worker}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test escalation
    task_description = "Build a complex SaaS dashboard"
    task_classification = classify_task(task_description)
    current_worker = "FCC"
    
    try:
        next_worker = escalate_worker(task_classification, current_worker)
        print(f"Escalated to Worker: {next_worker}")
    except ValueError as e:
        print(f"Escalation Error: {e}")