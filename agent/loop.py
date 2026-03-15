"""ReAct Agent loop = Reason + Act cycle """

import json
from typing import Any

from rich import print as rprint

from chat.provider import ChatProvider
from tools.registry import ToolRegistry

# added to the system prompt
_SYSTEM_SUFFIX = """
Available tools: {tools}.
Rules:
1. For greetings, opinions, and general knowledge questions, respond directly WITHOUT tools.
2. Only use tools when the user asks you to perform an action.
3. Call each tool ONCE. After getting the result, respond immediately.
"""

class AgentLoop:
    def __init__(self, provider: ChatProvider, registry: ToolRegistry, system_prompt: str = "", max_iterations: int = 10):
        self.provider = provider
        self.registry = registry
        self.max_iterations = max_iterations
        self.tool_defs = registry.get_definitions() or None
        self.system_prompt = system_prompt + _SYSTEM_SUFFIX.format(tools=", ".join(registry.tool_names))

    async def process(self, user_message: str) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Always send tool definitions — let the MODEL decide whether to use them
        seen_calls: dict[str, int] = {}
        tools_executed = 0

        for _ in range(self.max_iterations):
            response = await self.provider.chat(messages, tools=self.tool_defs)

            if response.content:
                rprint(f"[dim]💭 {response.content[:200]}[/]")

            # Model chose NOT to call any tool → return its direct answer
            if not response.has_tool_calls:
                return response.content

            # Model chose to call tool(s) → execute them
            assistant_msg: dict[str, Any] = {"role": "assistant", "content": response.content or ""}
            if response.raw_tool_calls:
                assistant_msg["tool_calls"] = response.raw_tool_calls
            messages.append(assistant_msg)

            has_new_call = False
            for tc in response.tool_calls:
                call_key = f"{tc.name}:{json.dumps(tc.arguments, sort_keys=True)}"
                seen_calls[call_key] = seen_calls.get(call_key, 0) + 1

                if seen_calls[call_key] > 1:
                    rprint(f"[yellow]⚠️ Duplicate: {tc.name} — skipping[/]")
                    messages.append({"role": "tool", "content": "Already called. Respond now.", "tool_call_id": tc.id})
                else:
                    has_new_call = True
                    rprint(f"[dim]🔧 {tc.name}({tc.arguments})[/]")
                    result = await self.registry.execute(tc.name, tc.arguments)
                    preview = result[:150] + "..." if len(result) > 150 else result
                    rprint(f"[dim]✅ {preview}[/]")
                    messages.append({"role": "tool", "content": result, "tool_call_id": tc.id})
                    tools_executed += 1

            # All calls were duplicates — force the model to answer with what it has
            if not has_new_call and tools_executed > 0:
                rprint("[yellow]⚠️ No new tools — forcing answer[/]")
                messages.append({"role": "user", "content": "Respond with the results now."})
                final = await self.provider.chat(messages, tools=None)
                return final.content

        return "⚠️ Max iterations reached."

