#!/usr/bin/env python3

def classify_task(task_description):
    task_classification = {
        "simple": False,
        "medium": False,
        "complex": False,
        "frontend": False,
        "backend": False,
        "full_stack": False,
        "debugging": False,
        "refactoring": False,
        "research": False,
        "testing": False
    }
    
    # Simple tasks (e.g., simple coding tasks)
    if "simple" in task_description.lower():
        task_classification["simple"] = True
    
    # Medium tasks (e.g., frontend development, debugging, refactoring)
    if "website" in task_description.lower() or "button" in task_description.lower():
        task_classification["frontend"] = True
        task_classification["medium"] = True
    
    if "debug" in task_description.lower() or "error" in task_description.lower():
        task_classification["debugging"] = True
        task_classification["medium"] = True
    
    if "refactor" in task_description.lower():
        task_classification["refactoring"] = True
        task_classification["medium"] = True
    
    # Complex tasks (e.g., full-stack development, complex SaaS)
    if "dashboard" in task_description.lower() or "SaaS" in task_description.lower():
        task_classification["complex"] = True
        task_classification["full_stack"] = True
    
    # Backend tasks
    if "backend" in task_description.lower() or "API" in task_description.lower():
        task_classification["backend"] = True
        if "complex" in task_description.lower():
            task_classification["complex"] = True
        else:
            task_classification["medium"] = True
    
    # Research tasks
    if "research" in task_description.lower():
        task_classification["research"] = True
        task_classification["medium"] = True
    
    # Testing tasks
    if "test" in task_description.lower():
        task_classification["testing"] = True
        task_classification["medium"] = True
    
    return task_classification