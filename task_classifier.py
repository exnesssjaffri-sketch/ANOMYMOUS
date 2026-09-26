#!/usr/bin/env python3

# Worker capabilities
WORKER_CAPABILITIES = {
    "FCC": ["implementation", "simple coding", "website creation", "bug fixes"],
    "Claude": ["architecture", "complex reasoning", "debugging", "code review"],
    "OpenCode": ["implementation", "frontend", "full-stack", "refactoring"],
}

# Worker registry
WORKER_REGISTRY = {
    "FCC": {"available": True, "command": "fcc", "version": "1.0"},
    "Claude": {"available": True, "command": "claude", "version": "2.0"},
    "OpenCode": {"available": True, "command": "opencode", "version": "1.1"},
}

def classify_task(task_description):
    task_classification = {
        "simple": False,
        "medium": False,
        "complex": False,
        "frontend": False,
        "backend": False,
        "full-stack": False,
        "debugging": False,
        "refactoring": False,
        "research": False,
        "testing": False
    }
    
    # Simple tasks (e.g., small coding tasks)
    if "simple" in task_description.lower() or "change" in task_description.lower() or "fix" in task_description.lower():
        task_classification["simple"] = True
    
    # Medium tasks (e.g., frontend development)
    if "website" in task_description.lower() or "button" in task_description.lower():
        task_classification["frontend"] = True
        task_classification["medium"] = True
    
    # Complex tasks (e.g., full-stack development)
    if "dashboard" in task_description.lower() or "SaaS" in task_description.lower():
        task_classification["complex"] = True
        task_classification["full-stack"] = True
    
    # Debugging tasks
    if "debug" in task_description.lower() or "error" in task_description.lower():
        task_classification["debugging"] = True
        task_classification["medium"] = True
    
    # Refactoring tasks
    if "refactor" in task_description.lower():
        task_classification["refactoring"] = True
        task_classification["medium"] = True
    
    # Research tasks
    if "research" in task_description.lower():
        task_classification["research"] = True
    
    # Testing tasks
    if "test" in task_description.lower():
        task_classification["testing"] = True
    
    return task_classification