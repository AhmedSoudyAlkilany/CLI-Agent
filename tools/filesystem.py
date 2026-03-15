"""Filesystem tools: read, write, list."""

from pathlib import Path
from typing import Any

from .base import Tool


class ReadFileTool(Tool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"},
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = Path(kwargs["path"])
        if not path.exists():
            return f"Error: File not found: {path}"
        try:
            content = path.read_text(encoding="utf-8")
            if len(content) > 10000:
                return content[:10000] + f"\n... (truncated, {len(content)} total chars)"
            return content
        except Exception as e:
            return f"Error reading file: {e}"


class WriteFileTool(Tool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file. Creates parent directories if needed."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = Path(kwargs["path"])
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(kwargs["content"], encoding="utf-8")
            return f"✅ Written to {path}"
        except Exception as e:
            return f"Error writing file: {e}"


class ListDirTool(Tool):
    @property
    def name(self) -> str:
        return "list_dir"

    @property
    def description(self) -> str:
        return "List files and directories in a path."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path", "default": "."},
            },
            "required": ["path"],
        }

    async def execute(self, **kwargs: Any) -> str:
        path = Path(kwargs.get("path", "."))
        if not path.exists():
            return f"Error: Path not found: {path}"
        try:
            items = []
            for p in sorted(path.iterdir()):
                prefix = "📁" if p.is_dir() else "📄"
                size = f" ({p.stat().st_size} bytes)" if p.is_file() else ""
                items.append(f"{prefix} {p.name}{size}")
            return "\n".join(items) if items else "(empty directory)"
        except Exception as e:
            return f"Error: {e}"
