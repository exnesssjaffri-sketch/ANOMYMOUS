import os
import shutil
from pathlib import Path
from typing import List, Optional

class WorkspaceManager:
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def _safe_path(self, relative_path: str) -> str:
        """
        Normalizes the path and ensures it's within the workspace boundary.
        """
        # Remove leading slashes and handle '..'
        normalized_rel = os.path.normpath(relative_path).lstrip(os.sep).lstrip("/")
        
        # Check for path escape attempts
        if normalized_rel.startswith("..") or os.path.isabs(normalized_rel):
            raise ValueError(f"Path escape detected: {relative_path}")
            
        # Also check for any '..' components in the path
        if ".." in normalized_rel.split(os.sep):
            raise ValueError(f"Path escape detected: {relative_path}")
            
        full_path = os.path.abspath(os.path.join(self.root_dir, normalized_rel))
        
        if not full_path.startswith(self.root_dir):
            raise ValueError(f"Path escape detected: {relative_path}")
            
        return full_path

    def write_file(self, path: str, content: str):
        full_path = self._safe_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read_file(self, path: str) -> str:
        full_path = self._safe_path(path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_files(self, path: str = ".") -> List[str]:
        full_path = self._safe_path(path)
        if not os.path.isdir(full_path):
            return []
        files = []
        for root, _, filenames in os.walk(full_path):
            for filename in filenames:
                rel_dir = os.path.relpath(root, self.root_dir)
                if rel_dir == ".":
                    files.append(filename)
                else:
                    files.append(os.path.join(rel_dir, filename))
        return files

    def delete_file(self, path: str):
        full_path = self._safe_path(path)
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)

    def exists(self, path: str) -> bool:
        full_path = self._safe_path(path)
        return os.path.exists(full_path)

    def get_full_path(self, path: str) -> str:
        return self._safe_path(path)
