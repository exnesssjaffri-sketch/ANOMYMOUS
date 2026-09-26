#!/usr/bin/env python3

import worker_registry

# Worker capabilities
WORKER_CAPABILITIES = {
    "FCC": ["simple", "implementation", "website creation", "bug fixes"],
    "Claude": ["architecture", "complex reasoning", "debugging", "code review"],
    "OpenCode": ["frontend", "full_stack", "implementation", "refactoring"],
}

def select_best_worker(task_classification):
    available_workers = [worker for worker in worker_registry.WORKER_REGISTRY if worker_registry.WORKER_REGISTRY[worker]["available"]]
    if not available_workers:
        raise ValueError("No available workers.")
    
    # Prioritize simple tasks with FCC
    if task_classification.get("simple", False):
        return "FCC"
    
    # Frontend tasks with OpenCode
    if task_classification.get("frontend", False):
        return "OpenCode"
    
    # Debugging tasks with Claude
    if task_classification.get("debugging", False):
        return "Claude"
    
    # Complex tasks with Claude
    if task_classification.get("complex", False):
        return "Claude"
    
    # Default to OpenCode for medium tasks
    return "OpenCode"

def escalate_worker(task_classification, current_worker):
    available_workers = [worker for worker in worker_registry.WORKER_REGISTRY if worker_registry.WORKER_REGISTRY[worker]["available"]]
    if not available_workers:
        raise ValueError("No available workers.")
    
    # Exclude the current worker
    available_workers = [worker for worker in available_workers if worker != current_worker]
    
    # Select the worker with the best match for the task
    best_worker = None
    best_match = -1
    
    for worker in available_workers:
        worker_capabilities = WORKER_CAPABILITIES[worker]
        match = sum(1 for capability in worker_capabilities if task_classification.get(capability, False))
        
        if match > best_match:
            best_match = match
            best_worker = worker
    
    return best_worker