#!/usr/bin/env python3
"""
流式输出 Web API (FastAPI + SSE)
用法: uv run python main_api.py
访问: http://localhost:8000/docs
"""
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


# 全局 Agent 实例 (生产环境请使用依赖注入)
agent_instance: Agent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global agent_instance
    agent_instance = Agent(
        session_id="web-session",
        name="web-assistant",
        system_prompt="你是一个本地用户助手，可以帮助用户处理本地工作。",
        llm=DeepSeek(model="deepseek-chat"),
        tools=[
            WeatherTool(),
            FileTool(work_dir=Path.cwd() / "work_dir"),
            TodoTool(),
        ],
        memory=Memory(),
    )
    print("Agent 服务已启动，访问 http://localhost:8000/docs 查看 API 文档")
    yield
    print("Agent 服务已关闭")


app = FastAPI(
    title="Learn Agent Streaming API",
    description="流式输出 Agent 服务",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def format_sse_event(data: dict) -> str:
    """将数据格式化为 SSE 格式"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_generator(user_input: str) -> AsyncGenerator[str, None]:
    """流式生成器"""
    if agent_instance is None:
        yield format_sse_event({"type": "error", "message": "Agent 未初始化"})
        return

    for event in agent_instance.run_stream(user_input):
        yield format_sse_event(event)


@app.post("/chat")
async def chat(request: Request):
    """
    流式对话接口

    请求体:
    {
        "message": "用户输入"
    }

    响应: SSE 流
    """
    body = await request.json()
    user_input = body.get("message", "")

    if not user_input:
        return StreamingResponse(
            iter([format_sse_event({"type": "error", "message": "消息不能为空"})]),
            media_type="text/event-stream",
        )

    return StreamingResponse(
        stream_generator(user_input),
        media_type="text/event-stream",
    )


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
