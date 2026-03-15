"""Chat provider with function calling support"""

import json 
from dataclasses import dataclass, field
from typing import Any

import litellm
from config.schema import Config

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass
class ChatResponse:
    content: str = ""
    model: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw_tool_calls : list[Any] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0
    
class ChatProvider:
    def __init__(self, config: Config):
        self.config = config
        self._setup_keys()

    def _setup_keys(self) -> None:
        import os
        for k, v in self.config.api_keys.items():
            if v:
                os.environ[k] = v

    async def chat(
            self,
            messages: list[dict[str, Any]],
            tools: list[dict[str, Any]] | None = None,
            model: str | None = None,
            **kwargs: Any,
        
            ) -> ChatResponse:
        model = model or self.config.chat.default_model
        call_args: dict[str, Any] = {
            "model" : model,
            "messages": messages,
            "temperature": self.config.chat.temperature,
            "max_tokens": self.config.chat.max_tokens,
            **kwargs,
        }
        if tools:
            call_args["tools"] = tools
            call_args["tool_choice"] = "auto"

        try:
            response = await litellm.acompletion(**call_args)
            choice = response.choices[0]
            msg = choice.message

            parsed_calls: list[ToolCall] = []
            raw_calls: list[Any] = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    args = tc.function.arguments
                    if isinstance(args, str):
                        args = tc.function.arguments
                    parsed_calls.append(ToolCall(id=tc.id, name=function.name, arguments=args))
                    raw_calls.append({"id": tc.id, "type": "function", "function":{"name": tc.function.name, "arguments":json.dumps(args)}})

            return ChatResponse(
                content=msg.content or "",
                model=response.model or model,
                tool_calls=parsed_calls,
                raw_tool_calls=raw_calls,
                usage=dict(response.usage) if response.usage else {},

            )
        except Exception as e:
            return ChatResponse(content=f"Error: {e}", model=model)