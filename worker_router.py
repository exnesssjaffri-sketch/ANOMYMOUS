#!/usr/bin/env python3

import os

# Worker capabilities
WORKER_CAPABILITIES = {
    "FCC": ["implementation", "simple coding", "website creation", "bug fixes"],
    "Claude": ["architecture", "complex reasoning", "debugging", "code review"],
    "OpenCode": ["implementation", "frontend", "full-stack", "refactoring"],
}

# Worker registry
from worker_registry import WORKER_REGISTRY

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
    available_workers = [worker for worker in WORKER_REGISTRY if WORKER_REGISTRY[worker]["available"]]
    if not available_workers:
        raise ValueError("No available workers.")
    
    # Exclude the current worker
    available_workers = [worker for worker in available_workers if worker != current_worker]
    
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