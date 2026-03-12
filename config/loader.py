"""Load Configuration"""
import json, os
from pathlib import Path
from dotenv import load_dotenv
from .schema import Config

def load_config(config_path: str = "config.json") -> Config:
    load_config()
    data: dict = {}
    path = Path(config_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    api_keys = data.get("api_keys", {})
    for env in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        val = os.getenv(env, "")
        if val:
            api_keys[env] = val
    data["api_keys"] = api_keys
    return Config(**data)