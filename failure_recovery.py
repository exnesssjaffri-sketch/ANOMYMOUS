#!/usr/bin/env python3

import os
from pathlib import Path
from typing import Dict, Any

# Failure recovery logic
def recover_from_failure(error_message: str, task_description: str, output_dir: str) -> Dict[str, Any]:
    repair_task = f"Fix the following error: {error_message}\n\nTask: {task_description}\n\nDo not modify unrelated files.\n\nAfter fixing, run the build again."
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Write repair task to a file
    repair_file_path = output_path / "repair_task.txt"
    with open(repair_file_path, "w") as file:
        file.write(repair_task)
    
    # Return structured recovery information
    return {
        "repair_task": repair_task,
        "repair_file_path": str(repair_file_path),
        "original_error": error_message,
        "original_task": task_description,
        "status": "repair_task_generated"
    }

if __name__ == "__main__":
    # Example usage for failure recovery
    error_message = "Module \"./Navbar\" not found."
    task_description = "Build a restaurant website"
    output_dir = str(Path.cwd() / "mock_output")
    
    # Generate repair task
    recovery_info = recover_from_failure(error_message, task_description, output_dir)
    print(f"Recovery Information: {recovery_info}")
    
    # Check if repair task file was created
    repair_file_path = Path(output_dir) / "repair_task.txt"
    if repair_file_path.exists():
        print("Repair task file created.")
    
    # Cleanup
    for file in Path(output_dir).iterdir():
        file.unlink()
    Path(output_dir).rmdir()