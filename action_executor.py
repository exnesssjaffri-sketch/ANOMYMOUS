import json
from typing import Dict, Any, Optional
from workspace_manager import WorkspaceManager
from process_executor import execute_process

class ActionExecutor:
    def __init__(self, workspace_manager: WorkspaceManager):
        self.workspace_manager = workspace_manager

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type")
        
        if action_type in ("create_file", "update_file"):
            return self._execute_write_file(action)
        elif action_type == "read_file":
            return self._execute_read_file(action)
        elif action_type == "list_directory":
            return self._execute_list_directory(action)
        elif action_type == "delete_file":
            return self._execute_delete_file(action)
        elif action_type in ("run_build", "run_test", "run_validation"):
            return self._execute_run_command(action)
        else:
            return {
                "status": "error",
                "error": f"Unsupported action type: {action_type}",
                "output": None
            }

    def _execute_write_file(self, action: Dict[str, Any]) -> Dict[str, Any]:
        path = action.get("path")
        content = action.get("content", "")
        if not path:
            return {"status": "error", "error": "Missing path", "output": None}
        try:
            self.workspace_manager.write_file(path, content)
            return {"status": "success", "output": f"File written to {path}", "error": None}
        except Exception as e:
            return {"status": "error", "error": str(e), "output": None}

    def _execute_read_file(self, action: Dict[str, Any]) -> Dict[str, Any]:
        path = action.get("path")
        if not path:
            return {"status": "error", "error": "Missing path", "output": None}
        try:
            content = self.workspace_manager.read_file(path)
            return {"status": "success", "output": content, "error": None}
        except Exception as e:
            return {"status": "error", "error": str(e), "output": None}

    def _execute_list_directory(self, action: Dict[str, Any]) -> Dict[str, Any]:
        path = action.get("path", ".")
        try:
            files = self.workspace_manager.list_files(path)
            return {"status": "success", "output": files, "error": None}
        except Exception as e:
            return {"status": "error", "error": str(e), "output": None}

    def _execute_delete_file(self, action: Dict[str, Any]) -> Dict[str, Any]:
        path = action.get("path")
        if not path:
            return {"status": "error", "error": "Missing path", "output": None}
        try:
            self.workspace_manager.delete_file(path)
            return {"status": "success", "output": f"Deleted {path}", "error": None}
        except Exception as e:
            return {"status": "error", "error": str(e), "output": None}

    def _execute_run_command(self, action: Dict[str, Any]) -> Dict[str, Any]:
        command = action.get("command")
        cwd = action.get("cwd")
        if not command:
            return {"status": "error", "error": "Missing command", "output": None}
        try:
            if isinstance(command, str):
                command = command.split()
            if cwd:
                cwd = self.workspace_manager.get_full_path(cwd)
            result = execute_process(command, cwd)
            return {
                "status": result["status"].lower(),
                "output": result["stdout"],
                "error": result["stderr"] if result["status"] != "SUCCESS" else None,
                "returncode": result["returncode"],
                "timed_out": result["timed_out"],
                "command_not_found": result["command_not_found"]
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "output": None}

    def execute_actions(self, actions: list) -> Dict[str, Any]:
        results = []
        for action in actions:
            result = self.execute_action(action)
            results.append(result)
            if result["status"] == "error" and action.get("critical", True):
                return {
                    "status": "error",
                    "error": result["error"],
                    "output": None,
                    "results": results
                }
        return {
            "status": "success",
            "output": "All actions completed",
            "error": None,
            "results": results
        }
