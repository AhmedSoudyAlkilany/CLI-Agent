"""Shell execution tool with timeout and safety"""

import asyncio
from typing import Any

from .base import Tool


class ExecTool(Tool):
    def __init__(self, timeout: int = 30, max_output: int = 5000):
        self.timeout = timeout
        self.max_output = max_output

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Execute a shell command. Returns stdout + stderr. Has a timeout."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"},
            },
            "required": ["command"],
        }

    async def execute(self, **kwargs: Any) -> str:
        command = kwargs["command"]
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.timeout
            )
            output = stdout.decode(errors="replace") + stderr.decode(errors="replace")
            if len(output) > self.max_output:
                output = output[:self.max_output] + "\n... (truncated)"
            return output if output.strip() else f"(exit code: {proc.returncode})"
        except asyncio.TimeoutError:
            proc.kill()
            return f"Error: Command timed out after {self.timeout}s"
        except Exception as e:
            return f"Error: {e}"
