#!/usr/bin/env python3
"""
流式输出 CLI 入口
用法: uv run python main_stream.py
"""
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

    full_response = ""

    for event in agent.run_stream(user_input):
        event_type = event.get("type")

        if event_type == "assistant":
            # 助手回复片段
            content = event["content"]
            print(content, end="", flush=True)
            full_response += content

        elif event_type == "tool_call":
            # 工具调用开始
            tool_name = event["name"]
            print(f"\n\n[正在调用工具: {tool_name}]", flush=True)

        elif event_type == "tool_result":
            # 工具执行完成
            tool_name = event["name"]
            result = event["result"]
            # 简短显示结果
            result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            print(f"[工具 {tool_name} 执行完成]: {result_preview}\n", flush=True)
            print("助手: ", end="", flush=True)

        elif event_type == "tool_error":
            # 工具执行错误
            tool_name = event["name"]
            error = event["error"]
            print(f"\n[工具 {tool_name} 错误]: {error}\n", flush=True)
            print("助手: ", end="", flush=True)

        elif event_type == "done":
            # 完成
            final = event.get("final", "")
            print("\n" + "=" * 60)
            break

        elif event_type == "error":
            # 错误
            print(f"\n错误: {event['message']}")
            break

    return full_response


def main():
    agent = Agent(
        session_id="stream-session",
        name="stream-assistant",
        system_prompt="你是一个本地用户助手，可以帮助用户处理本地工作。请简洁回答。",
        llm=DeepSeek(model="deepseek-chat"),
        tools=[
            WeatherTool(),
            FileTool(work_dir=Path.cwd() / "work_dir"),
            TodoTool(),
        ],
        memory=Memory(),
    )

    print("流式助手已启动 (输入 'quit' 退出)")
    print("-" * 40)

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出")
            break

        if not user_input:
            continue

        if user_input.lower() in ["quit", "exit", "q"]:
            print("再见!")
            break

        stream_output(agent, user_input)


if __name__ == "__main__":
    main()
