"""Tool registry — manages tool registration and execution"""

import json
from typing import Any

from .base import Tool


class ToolRegistry:
    """Central registry for all available tools"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def get_definitions(self) -> list[dict[str, Any]]:
        """Get all tool definitions for LLM function calling"""
        return [t.to_function_def() for t in self._tools.values()]

    async def execute(self, name: str, arguments: dict[str, Any] | str) -> str:
        """Execute a tool by name with given arguments"""
        tool = self._tools.get(name)
        if not tool:
            return f"Error: Tool '{name}' not found. Available: {self.tool_names}"

        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON arguments for '{name}'"

        try:
            return await tool.execute(**arguments)
        except Exception as e:
            return f"Error executing '{name}': {e}"
