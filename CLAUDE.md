# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A lightweight Agent system tutorial project implementing core Agent concepts: LLM, Toolkit, Memory, and Agent orchestration. Built for learning purposes with Python 3.13+.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the main application (requires .env with DEEPSEEK_API_KEY)
uv run main.py

# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_tool/test_file.py

# Run with dev dependencies
uv run --group dev pytest
```

## Architecture

The agent system follows a modular design pattern:

```
Agent (orchestrator)
├── LLM (model provider)
│   └── DeepSeek (extends LLM with DeepSeek API config)
├── Memory (conversation context storage)
└── Toolkit (tool collections)
    └── Individual tools: FileTool, TodoTool, SubAgentTool, WeatherTool
```

**Core flow in `Agent.run()`:**
1. Add user message to Memory
2. Get all tool schemas from Toolkits
3. Loop up to `max_tool_rounds`:
   - Call LLM with current context and tools
   - If no tool calls, return response
   - Execute each tool call via `_dispatch_tool()`
   - Add tool results back to Memory as `role="tool"`
4. Return final response or error if max rounds reached

**Tool system (`learn_agent/tool/toolkit.py`):**
- `Toolkit` base class stores functions and generates OpenAI-compatible schemas
- `function_to_tool_schema()` converts Python functions to tool definitions
- Tools are registered by passing callables to Toolkit constructor

**LLM abstraction (`learn_agent/llm.py`):**
- `LLM` base class wraps OpenAI client
- `DeepSeek` subclass configures DeepSeek API endpoint
- `chat()` method accepts messages and optional tools, returns AssistantMessage

## Key Files

- `learn_agent/agent/agent.py:42` - Main `run()` method with tool execution loop
- `learn_agent/tool/toolkit.py:65` - Toolkit base class
- `learn_agent/tool/file_tool.py` - FileTool implementation (read/write/bash)
- `learn_agent/tool/todo_tool.py` - TodoTool for task management
- `learn_agent/tool/subagent_tool.py` - SubAgentTool for nested agent execution

## Configuration

- Copy `.env.example` to `.env` and set `DEEPSEEK_API_KEY`
- Python path configured via `pyproject.toml` with `pythonpath = ["."]`


## Test
- uv run pytest
- can use @pytest.fixture