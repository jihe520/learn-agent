import json
from typing import Any
from learn_agent.llm import LLM
from learn_agent.memory import Memory
from learn_agent.tool.toolkit import Toolkit


class Agent:
    def __init__(
        self,
        llm: LLM,
        session_id: str,
        name: str,
        tools: list[Toolkit],
        memory: Memory,
        system_prompt: str = "",
    ):
        self.session_id = session_id
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.max_tool_rounds = 8

        self.memory.add_message(role="system", content=system_prompt)

    def _all_tool_schemas(self) -> list[dict]:
        # 汇总所有工具的 schema，给模型识别可调用的工具
        schemas = []
        for toolkit in self.tools:
            schemas.extend(toolkit.list_tools_schemas())
        return schemas

    def _dispatch_tool(self, tool_name: str, args: dict) -> Any:
        # 找到具体工具并执行
        for toolkit in self.tools:
            if toolkit.has(tool_name):
                return toolkit.call(tool_name, **args)
        raise ValueError(f"Tool {tool_name} not found in any toolkit.")

    def run(self, user_text: str) -> str:
        # 把用户输入加入上下文
        self.memory.add_message(role="user", content=user_text)

        tool_schema = self._all_tool_schemas()

        for _round in range(self.max_tool_rounds):
            # 每一轮都带上当前上下文让模型决定是否要调用工具
            messages = self.memory.get_context()

            # 进行一次对话请求
            msg = self.llm.chat(messages=messages, tools=tool_schema)

            # 处理模型返回的信息,其是assistant角色的消息
            assistant_dict = {"role": "assistant"}
            if getattr(msg, "content", None) is not None:
                assistant_dict["content"] = msg.content

            # 如果模型返回了工具调用信息，也要重新加入上下文，作为assistant消息的一部分
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                assistant_dict["tool_calls"] = [tc.model_dump() for tc in tool_calls]

            self.memory.add_message(**assistant_dict)

            # 在此你可以添加反思 reflection 逻辑，决定是否继续调用工具
            if not tool_calls:
                # 没有调用工具，结束
                return msg.content or ""

            # 如果有工具调用，逐个执行，并把结果作为 role="tool" 回填到上下文
            for tc in tool_calls:
                # 解析模型返回的工具调用信息
                tc_id = tc.id
                fn_name = tc.function.name
                raw_args = tc.function.arguments or "{}"

                try:
                    # arguments 可能是 JSON 字符串
                    args = (
                        json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    )
                except Exception:
                    args = {}

                try:
                    # 执行本地工具函数
                    result = self._dispatch_tool(fn_name, args)
                    # 工具结果以更“模型友好”的结构回填
                    tool_content = json.dumps(
                        {"ok": True, "result": result}, ensure_ascii=False
                    )
                except Exception as e:
                    tool_content = json.dumps(
                        {
                            "ok": False,
                            "error": {"code": "TOOL_EXEC_ERROR", "message": str(e)},
                        },
                        ensure_ascii=False,
                    )

                self.memory.add_message(
                    role="tool",
                    content=tool_content,
                    tool_call_id=tc_id,
                )

        return "ERROR: reached maximum tool rounds without a final answer."
