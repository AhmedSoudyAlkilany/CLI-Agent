"""ReAct CLI Agent"""

import asyncio
from typing import Optional
import typer
from rich import print as rprint
from rich.panel import Panel
from rich.prompt import Prompt

from config.loader import load_config
from chat.provider import ChatProvider
from tools.registry import ToolRegistry
from tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from tools.shell import ExecTool
from tools.web import WebSearchTool, WebFetchTool
from agent.loop import AgentLoop

app = typer.Typer(help="🤖 ReAct Agent")

@app.callback()
def callback():
    pass

def _build_agent(model: str | None = None) -> AgentLoop:
    config = load_config()
    if model:
        config.chat.default_model = model
    provider = ChatProvider(config)
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirTool())
    registry.register(ExecTool(timeout=config.tools.exec_timeout))
    registry.register(WebSearchTool())
    registry.register(WebFetchTool())
    return AgentLoop(provider=provider, registry=registry, system_prompt=config.chat.system_prompt)

@app.command()
def agent(
    message: Optional[str] = typer.Option(None, "-m"),
    interactive: bool = typer.Option(False, "-i"),
    model: Optional[str] = typer.Option(None, "--model"),
):
    """AI agent with tools. 🛠️"""
    loop = _build_agent(model)
    if interactive:
        asyncio.run(_interactive(loop))
    elif message:
        asyncio.run(_single(loop, message))
    else:
        rprint("[yellow]Use -m 'msg' or -i for interactive[/]")


async def _interactive(loop: AgentLoop) -> None:
    rprint(Panel("🛠️ ReAct Agent", border_style="green"))
    while True:
        try:
            user_input = Prompt.ask("[green]You[/]")
        except (KeyboardInterrupt, EOFError):
            break
        if user_input.strip().lower() in ("exit", "quit"):
            break
        if not user_input.strip():
            continue
        rprint("[dim]⏳ Thinking...[/]")
        response = await loop.process(user_input)
        rprint(f"\n[blue]🤖[/] {response}\n")


async def _single(loop: AgentLoop, message: str) -> None:
    response = await loop.process(message)
    rprint(f"[blue]🤖[/] {response}")


if __name__ == "__main__":
    app()
