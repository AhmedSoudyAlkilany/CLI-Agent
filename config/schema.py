"""Configuration schema."""
from pydantic import BaseModel, Field

class ToolsConfig(BaseModel):
    exec_timeout: int = 30
    max_output: int = 5000

class ChatConfig(BaseModel):
    default_model:str = "ollama/llama3.2:3b"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = (
        "You are a helpful AI agent with access to tools. "
        "When a user asks you to do something, use the appropriate tool. "
        "After getting the tool result, respond to the user with a clear answer. "
        "Do NOT call the same tool repeatedly. If you have the answer, respond directly."
    )

class Config(BaseModel):
    chat: ChatConfig = Field(default_factory=ChatConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    api_keys: dict[str, str] = Field(default_factory=dict)