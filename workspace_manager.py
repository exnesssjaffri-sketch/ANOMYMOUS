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
        Normalize a workspace-relative path and enforce the boundary.

        commonpath avoids sibling-prefix mistakes (for example, /work vs
        /workspace-evil), while realpath also resolves symlinks before the
        boundary check.
        """
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError("A non-empty relative path is required")

        # Reject absolute paths and parent traversal rather than silently
        # rewriting them into a different path.
        if os.path.isabs(relative_path) or os.path.splitdrive(relative_path)[0]:
            raise ValueError(f"Path escape detected: {relative_path}")

        normalized_rel = os.path.normpath(relative_path)
        components = normalized_rel.replace("\\", "/").split("/")
        if normalized_rel in (".", ""):
            normalized_rel = "."
        elif any(part == ".." for part in components):
            raise ValueError(f"Path escape detected: {relative_path}")

        root = os.path.realpath(self.root_dir)
        full_path = os.path.realpath(os.path.join(root, normalized_rel))
        try:
            if os.path.commonpath([root, full_path]) != root:
                raise ValueError(f"Path escape detected: {relative_path}")
        except ValueError:
            # commonpath raises when paths are on different drives.
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
