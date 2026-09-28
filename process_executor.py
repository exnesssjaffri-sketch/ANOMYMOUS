import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def execute_process(command: list[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a command in a subprocess with strict safety and timeout.
    
    Args:
        command: List of command arguments (no shell interpolation).
        cwd: Working directory for the subprocess. If None, uses current directory.
    
    Returns:
        Dict[str, Any] with:
            - status: "SUCCESS", "FAILED", "TIMEOUT", or "COMMAND_NOT_FOUND"
            - returncode: Actual subprocess return code (0 for success, non-zero for failure)
            - stdout: Captured stdout (str)
            - stderr: Captured stderr (str)
            - timed_out: Whether the process timed out
            - command_not_found: Whether the command was not found
    """
    result = {
        "status": "COMMAND_NOT_FOUND",
        "returncode": -1,
        "stdout": "",
        "stderr": "",
        "timed_out": False,
        "command_not_found": False
    }
    
    # Resolve cwd to an existing directory
    if cwd is None:
        cwd = os.getcwd()
    
    try:
        # Check if cwd is a directory
        if not os.path.isdir(cwd):
            raise ValueError(f"Invalid workspace: {cwd} is not a directory")
        
        # Execute the command with strict safety
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False  # Never use shell=True
            )
            
            # Wait for the process with timeout
            try:
                stdout, stderr = process.communicate(timeout=10)
                result["stdout"] = stdout
                result["stderr"] = stderr
                
                if process.returncode == 0:
                    result["status"] = "SUCCESS"
                    result["returncode"] = process.returncode
                else:
                    result["status"] = "FAILED"
                    result["returncode"] = process.returncode
                    
            except subprocess.TimeoutExpired:
                process.kill()  # Terminate the process
                result["status"] = "TIMEOUT"
                result["timed_out"] = True
                result["returncode"] = -1  # Timeout
                
        except FileNotFoundError:
            result["status"] = "COMMAND_NOT_FOUND"
            result["command_not_found"] = True
            result["returncode"] = -1
            
    except Exception as e:
        # Fallback for unexpected errors (e.g., permission issues)
        result["status"] = "FAILED"
        result["stderr"] = f"Unexpected error: {str(e)}"
        result["returncode"] = -1
    
    return result
