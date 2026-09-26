#!/usr/bin/env python3

import os

# Failure recovery logic
def recover_from_failure(error_message, task_description, output_dir):
    repair_task = f"Fix the following error: {error_message}\n\nTask: {task_description}\n\nDo not modify unrelated files.\n\nAfter fixing, run the build again."
    
    # Write repair task to a file
    with open(os.path.join(output_dir, "repair_task.txt"), "w") as file:
        file.write(repair_task)
    
    return repair_task

if __name__ == "__main__":
    # Example usage for failure recovery
    error_message = "Module \"./Navbar\" not found."
    task_description = "Build a restaurant website"
    output_dir = os.path.join(os.getcwd(), "mock_output")
    
    # Create mock output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate repair task
    repair_task = recover_from_failure(error_message, task_description, output_dir)
    print(f"Repair Task: {repair_task}")
    
    # Check if repair task file was created
    repair_file_path = os.path.join(output_dir, "repair_task.txt")
    if os.path.exists(repair_file_path):
        print("Repair task file created.")
    
    # Cleanup
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    os.rmdir(output_dir)