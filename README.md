# CLI Agent

A small, modular command-line agent built in Python. It follows a Reason + Act loop: the model proposes steps, then executes tools to make progress. The codebase is intentionally straightforward so it is easy to extend.

## Features
- ReAct-style loop with tool execution
- Tool registry with a simple interface
- CLI modes for one-shot and interactive runs
- Built-in tools: file read/write/list, shell exec, web search, and web fetch

## Requirements
- Python 3.10+

## Quickstart
1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run the agent.

```bash
python main.py agent -m "Summarize this repo."
```

## Usage
One-shot:

```bash
python main.py agent -m "Find TODOs in this project."
```

Interactive:

```bash
python main.py agent -i
```

Select a model (optional):

```bash
python main.py agent -m "Hello" --model gpt-4o-mini
```

## Configuration
`config.json` is read at startup. API keys can be provided via environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

## Project Structure
- `main.py` - CLI entry point and tool registration
- `agent/` - ReAct loop and orchestration
- `tools/` - tool implementations (filesystem, shell, web)
- `config/` - config loader and schema

