# 流式输出 (Streaming)

本教程介绍如何为 Agent 添加流式输出支持，实现逐字显示效果。

## 1. 概述

流式输出是指模型生成内容时，无需等待完整响应即可逐步返回数据。这种方式能提供更好的用户体验，让用户即时看到生成进度。

### 1.1 应用场景

| 场景 | 说明 |
|------|------|
| CLI 终端 | 逐字打印输出效果，实时显示思考过程 |
| Web API | SSE (Server-Sent Events) 流式传输，支持网页实时显示 |

### 1.2 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      现有架构 (保持不变)                      │
├─────────────────────────────────────────────────────────────┤
│  Agent.run() → str (同步阻塞，返回完整响应)                   │
│  LLM.chat() → ChatCompletionMessage (stream=False)          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     新增流式架构                              │
├─────────────────────────────────────────────────────────────┤
│  Agent.run_stream() → Generator[dict, None, None]           │
│  LLM.chat_stream() → Generator[ChatCompletionChunk]         │
└─────────────────────────────────────────────────────────────┘
```

## 2. 核心实现

### 2.1 LLM 层：添加流式方法

在 `LLM` 类中添加 `chat_stream()` 方法：

```python
# learn_agent/llm.py
from typing import Generator

class LLM:
    # ... 现有代码不变 ...

    def chat_stream(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> Generator[dict, None, None]:
        """
        流式对话方法，返回生成器

        Yields:
            dict: 包含不同类型事件的字典
                - {"type": "content", "content": "xxx"}  # 内容片段
                - {"type": "tool_calls", "tool_calls": [...]}  # 工具调用
                - {"type": "done"}  # 流结束
        """
        kwargs = dict(
            model=self.model,
            messages=messages,
            stream=True,  # 关键：启用流式
        )

        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)

        content_buffer = ""
        tool_calls_buffer: dict[int, dict] = {}

        for chunk in response:
            delta = chunk.choices[0].delta

            # 处理内容块
            if delta.content:
                content_chunk = delta.content
                content_buffer += content_chunk
                yield {"type": "content", "content": content_chunk}

            # 处理工具调用块
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    tc_index = tc.index
                    if tc_index not in tool_calls_buffer:
                        tool_calls_buffer[tc_index] = {
                            "id": "",
                            "type": "",
                            "function": {"name": "", "arguments": ""},
                        }

                    if tc.id:
                        tool_calls_buffer[tc_index]["id"] = tc.id
                    if tc.function and tc.function.name:
                        tool_calls_buffer[tc_index]["function"]["name"] = tc.function.name
                    if tc.function and tc.function.arguments:
                        tool_calls_buffer[tc_index]["function"]["arguments"] += tc.function.arguments

        # 流结束，输出完整工具调用信息
        if tool_calls_buffer:
            tool_calls_list = [tool_calls_buffer[i] for i in sorted(tool_calls_buffer.keys())]
            yield {"type": "tool_calls", "tool_calls": tool_calls_list}

        yield {"type": "done"}
```

关键点：
- `stream=True` 启用流式模式
- 遍历 `response` 获取每个数据块 (`chunk`)
- 使用 `yield` 逐步产出内容片段
- 工具调用需要组装分块返回的数据

### 2.2 Agent 层：添加流式方法

在 `Agent` 类中添加 `run_stream()` 方法：

```python
# learn_agent/agent/agent.py
from typing import Generator

class Agent:
    # ... 现有代码不变 ...

    def run_stream(
        self, user_text: str
    ) -> Generator[dict, None, None]:
        """
        流式运行方法

        Yields:
            dict: 事件字典
                - {"type": "assistant", "content": "xxx"}  # 助手回复片段
                - {"type": "tool_call", "name": "xxx", "args": {...}}  # 工具调用开始
                - {"type": "tool_result", "name": "xxx", "result": {...}}  # 工具执行结果
                - {"type": "done", "final": "xxx"}  # 完成
                - {"type": "error", "message": "xxx"}  # 错误
        """
        # 把用户输入加入上下文
        self.memory.add_message(role="user", content=user_text)
        yield {"type": "user_message", "content": user_text}

        tool_schema = self._all_tool_schemas()

        for _round in range(self.max_tool_rounds):
            messages = self.memory.get_context()

            # 使用流式 LLM 调用
            assistant_content_buffer = ""
            tool_calls_info: list[dict] = []

            for event in self.llm.chat_stream(messages=messages, tools=tool_schema):
                event_type = event.get("type")

                if event_type == "content":
                    content_chunk = event["content"]
                    assistant_content_buffer += content_chunk
                    yield {"type": "assistant", "content": content_chunk}

                elif event_type == "tool_calls":
                    tool_calls_info = event["tool_calls"]

                elif event_type == "done":
                    break

            # 处理工具调用（如果有）
            if tool_calls_info:
                for tc in tool_calls_info:
                    fn_name = tc["function"]["name"]
                    raw_args = tc["function"]["arguments"]

                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        args = {}

                    # 发送工具调用开始事件
                    yield {"type": "tool_call", "name": fn_name, "args": args}

                    # 执行工具
                    try:
                        result = self._dispatch_tool(fn_name, args)
                        yield {"type": "tool_result", "name": fn_name, "result": result}
                    except Exception as e:
                        yield {"type": "tool_error", "name": fn_name, "error": str(e)}

                    # 添加到上下文
                    self.memory.add_message(
                        role="tool",
                        content=json.dumps({"ok": True, "result": result}, ensure_ascii=False),
                        tool_call_id=tc["id"],
                    )

                continue

            # 没有工具调用，任务完成
            self.memory.add_message(role="assistant", content=assistant_content_buffer)
            yield {"type": "done", "final": assistant_content_buffer}
            return

        # 达到最大轮次
        yield {"type": "error", "message": "ERROR: reached maximum tool rounds"}
```

事件类型设计：

| 事件类型 | 字段 | 说明 |
|---------|------|------|
| `assistant` | `content` | 助手回复内容片段 |
| `tool_call` | `name`, `args` | 工具调用开始 |
| `tool_result` | `name`, `result` | 工具执行结果 |
| `tool_error` | `name`, `error` | 工具执行错误 |
| `done` | `final` | 任务完成 |
| `error` | `message` | 错误信息 |

## 3. CLI 流式输出

创建 `main_stream.py` 实现交互式流式输出：

```python
#!/usr/bin/env python3
"""流式输出 CLI 入口"""
from pathlib import Path

from learn_agent.agent.agent import Agent
from learn_agent.llm import DeepSeek
from learn_agent.memory import Memory
from learn_agent.tool.weather_tool import WeatherTool
from learn_agent.tool.file_tool import FileTool
from learn_agent.tool.todo_tool import TodoTool


def stream_output(agent: Agent, user_input: str):
    """流式输出处理器"""
    print("\n" + "=" * 60)
    print("助手: ", end="", flush=True)

    for event in agent.run_stream(user_input):
        event_type = event.get("type")

        if event_type == "assistant":
            content = event["content"]
            print(content, end="", flush=True)

        elif event_type == "tool_call":
            tool_name = event["name"]
            print(f"\n\n[正在调用工具: {tool_name}]", flush=True)

        elif event_type == "tool_result":
            tool_name = event["name"]
            result = event["result"]
            result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            print(f"[工具 {tool_name} 执行完成]: {result_preview}\n", flush=True)
            print("助手: ", end="", flush=True)

        elif event_type == "done":
            print("\n" + "=" * 60)
            break


def main():
    agent = Agent(
        session_id="stream-session",
        name="stream-assistant",
        system_prompt="你是一个本地用户助手，请简洁回答。",
        llm=DeepSeek(model="deepseek-chat"),
        tools=[WeatherTool(), FileTool(work_dir=Path.cwd() / "work_dir"), TodoTool()],
        memory=Memory(),
    )

    print("流式助手已启动 (输入 'quit' 退出)")
    print("-" * 40)

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("再见!")
            break
        stream_output(agent, user_input)


if __name__ == "__main__":
    main()
```

运行方式：

```bash
uv run python main_stream.py
```

输出效果：

```
====================================================================================================
助手: 好的，我来帮你查看当前文件夹的文件。

[正在调用工具: bash]
[工具 bash 执行完成]: {'stdout': 'docs/  main.py  main_api.py  main_stream.py  pyproject.toml...}

助手: 当前文件夹包含以下内容：
- docs/ 目录
- main.py  主入口
- main_stream.py  流式 CLI
- main_api.py  Web API
====================================================================================================
```

## 4. Web API 流式输出 (SSE)

### 4.1 添加 FastAPI 依赖

```bash
uv add fastapi sse-starlette uvicorn
```

### 4.2 创建 Web 服务

创建 `main_api.py`：

```python
#!/usr/bin/env python3
"""流式输出 Web API (FastAPI + SSE)"""
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from learn_agent.agent.agent import Agent
from learn_agent.llm import DeepSeek
from learn_agent.memory import Memory
from learn_agent.tool.weather_tool import WeatherTool
from learn_agent.tool.file_tool import FileTool
from learn_agent.tool.todo_tool import TodoTool
from pathlib import Path


agent_instance: Agent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    agent_instance = Agent(
        session_id="web-session",
        name="web-assistant",
        system_prompt="你是一个本地用户助手。",
        llm=DeepSeek(model="deepseek-chat"),
        tools=[WeatherTool(), FileTool(work_dir=Path.cwd() / "work_dir"), TodoTool()],
        memory=Memory(),
    )
    yield


app = FastAPI(title="Learn Agent Streaming API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def format_sse_event(data: dict) -> str:
    """将数据格式化为 SSE 格式"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_generator(user_input: str) -> AsyncGenerator[str, None]:
    if agent_instance is None:
        yield format_sse_event({"type": "error", "message": "Agent 未初始化"})
        return

    for event in agent_instance.run_stream(user_input):
        yield format_sse_event(event)


@app.post("/chat")
async def chat(request: Request):
    """流式对话接口"""
    body = await request.json()
    user_input = body.get("message", "")

    if not user_input:
        return StreamingResponse(
            iter([format_sse_event({"type": "error", "message": "消息不能为空"})]),
            media_type="text/event-stream",
        )

    return StreamingResponse(stream_generator(user_input), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4.3 启动服务

```bash
uv run python main_api.py
```

访问 http://localhost:8000/docs 查看 Swagger API 文档。

### 4.4 SSE 客户端示例

```javascript
async function sendMessage() {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: "你好" })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                console.log(data);
            }
        }
    }
}
```

## 5. 事件流格式

SSE 响应格式如下：

```
data: {"type": "user_message", "content": "你好"}

data: {"type": "assistant", "content": "你"}

data: {"type": "assistant", "content": "好，"}

data: {"type": "assistant", "content": "有什么"}

data: {"type": "assistant", "content": "可以帮"}

data: {"type": "assistant", "content": "你的"}

data: {"type": "tool_call", "name": "get_weather", "args": {"city": "北京"}}

data: {"type": "tool_result", "name": "get_weather", "result": {"temperature": "25°C", "weather": "晴"}}

data: {"type": "done", "final": "你好，有什么可以帮你的吗？"}
```

## 6. 小结

| 组件 | 文件 | 新增方法 |
|------|------|----------|
| LLM | `learn_agent/llm.py` | `chat_stream()` |
| Agent | `learn_agent/agent/agent.py` | `run_stream()` |
| CLI | `main_stream.py` | - |
| Web API | `main_api.py` | `/chat` (SSE) |

### 关键设计原则

1. **向后兼容**：现有 `run()` 和 `chat()` 方法保持不变
2. **事件驱动**：使用事件类型区分不同数据
3. **工具可见**：流式显示工具调用过程，提升透明度
4. **双端支持**：CLI 和 Web API 统一使用事件流格式
