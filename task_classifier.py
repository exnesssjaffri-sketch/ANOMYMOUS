#!/usr/bin/env python3

# Task classification logic
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
    if "change" in task_description.lower() or "fix" in task_description.lower():
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

if __name__ == "__main__":
    task_description = "Build a simple website with a button"
    task_classification = classify_task(task_description)
    print(f"Task Classification: {task_classification}")
    
    task_description = "Fix a broken import"
    task_classification = classify_task(task_description)
    print(f"Task Classification: {task_classification}")
    
    task_description = "Build a complex SaaS dashboard"
    task_classification = classify_task(task_description)
    print(f"Task Classification: {task_classification}")