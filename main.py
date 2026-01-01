from typing import Callable, Any
from openai import OpenAI
import os
from dotenv import load_dotenv
from icecream import ic
import inspect
import json

load_dotenv()


class LLM:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat(self, messages: list[dict], tools: list[dict] | None = None):
        kwargs = dict(
            model=self.model,
            messages=messages,
            stream=False,
        )

        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens
        if tools:
            kwargs["tools"] = tools
            # kwargs["tool_choice"] = "auto"  # 一般默认就是 auto，可显式打开

        response = self.client.chat.completions.create(**kwargs)
        ic(response)
        msg = response.choices[0].message
        return msg


class DeepSeek(LLM):
    def __init__(
        self,
        api_key: str | None = os.getenv("DEEPSEEK_API_KEY"),
        model: str | None = "deepseek-chat",
    ):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.deepseek.com",
        )


def _py_type_to_json_type(t: Any) -> str:
    # 极简映射：够用即可（你后面可以扩展）
    if t in (int,):
        return "integer"
    if t in (float,):
        return "number"
    if t in (bool,):
        return "boolean"
    if t in (str,):
        return "string"
    return "string"


def function_to_tool_schema(fn: Callable[..., Any]) -> dict:
    """
    把一个 Python 函数转成 OpenAI tools function schema（最小版）
    - 参数从签名拿
    - description 用 docstring 第一段
    """
    sig = inspect.signature(fn)
    props: dict[str, Any] = {}
    required: list[str] = []

    for name, p in sig.parameters.items():
        if name == "self":
            continue
        ann = p.annotation if p.annotation is not inspect._empty else str
        # 处理 Optional[...] / Union[...]：这里只做最小化，统一按 string/number/integer 走
        json_type = _py_type_to_json_type(
            ann if ann in (int, float, bool, str) else str
        )
        props[name] = {"type": json_type}

        if p.default is inspect._empty:
            required.append(name)

    doc = inspect.getdoc(fn) or ""
    fn_name = getattr(fn, "__name__", fn.__class__.__name__)
    desc = doc.strip().split("\n\n")[0] if doc.strip() else f"Call {fn_name}"

    return {
        "type": "function",
        "function": {
            "name": fn_name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        },
    }


class Toolkit:
    def __init__(
        self,
        name: str | None = None,
        tools: list[Callable] | None = None,
    ):
        self.name = name or self.__class__.__name__
        self._tools: dict[str, Callable] = {}
        if tools:
            for fn in tools:
                fn_name = getattr(fn, "__name__", fn.__class__.__name__)
                self._tools[fn_name] = fn

    def list_tools_schemas(self) -> list[dict]:
        return [function_to_tool_schema(fn) for fn in self._tools.values()]

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def call(self, tool_name: str, **kwargs) -> Any:
        if not self.has(tool_name):
            raise ValueError(f"Tool {tool_name} not found in toolkit {self.name}")
        fn = self._tools[tool_name]
        return fn(**kwargs)


class WeatherTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="WeatherTool",
            tools=[self.get_temperature, self.get_humidity],
        )

    def get_temperature(self, num: int | None = 2) -> list[dict[str, float]]:
        """
        获取几天的温度

        Args:
            num (int | None): 天数，默认2天
        Returns:
            list[dict[str, float]]: 日期和温度对应的列表
        """
        return [{"2024-01-01": 25.0}, {"2024-01-02": 26.5}]

    def get_humidity(self, num: int | None = 2) -> list[dict[str, float]]:
        """
        获取几天的湿度

        Args:
            num (int | None): 天数，默认2天
        Returns:
            list[dict[str, float]]: 日期和湿度对应的列表
        """
        return [{"2024-01-01": 60.0}, {"2024-01-02": 65.0}]


class FileTool(Toolkit):
    def __init__(self, work_dir: str = "."):
        self.work_dir = os.path.abspath(work_dir)
        super().__init__(
            name="FileTool",
            tools=[self.create_file, self.list_files],
        )

    def create_file(self, filename: str, content: str):
        """
        创建一个Markdown文件并写入初始内容

        Args:
            filename (str): 文件名
            content (str): 文件内容
        Returns:
            str: 创建文件的结果信息
        """
        with open(filename, "w") as f:
            f.write(content)
        return f"File '{filename}' created successfully and content written."

    def list_files(self, dir: str):
        """
        列出指定目录下的所有文件和文件夹

        Args:
            dir (str): 目录路径
        Returns:
            list[str]: 目录下的文件和文件夹列表
        """
        return os.listdir(dir)  # 当前目录


class Memory:
    def __init__(self):
        self.messages: list[dict] = []

    def add_message(self, role: str, content: str | None = None, **extra):
        msg = {"role": role}
        if content is not None:
            msg["content"] = content
        msg.update(extra)
        self.messages.append(msg)

    def get_context(self) -> list[dict]:
        return self.messages


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
        schemas = []
        for toolkit in self.tools:
            schemas.extend(toolkit.list_tools_schemas())
        return schemas

    def _dispatch_tool(self, tool_name: str, args: dict) -> Any:
        for toolkit in self.tools:
            if toolkit.has(tool_name):
                return toolkit.call(tool_name, **args)
        raise ValueError(f"Tool {tool_name} not found in any toolkit.")

    def run(self, user_text: str) -> str:
        self.memory.add_message(role="user", content=user_text)

        tool_schema = self._all_tool_schemas()

        for _round in range(self.max_tool_rounds):
            messages = self.memory.get_context()

            msg = self.llm.chat(messages=messages, tools=tool_schema)

            assistant_dict = {"role": "assistant"}
            if getattr(msg, "content", None) is not None:
                assistant_dict["content"] = msg.content

            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                assistant_dict["tool_calls"] = [tc.model_dump() for tc in tool_calls]

            self.memory.add_message(**assistant_dict)

            if not tool_calls:
                # 没有调用工具，结束
                return msg.content or ""

            for tc in tool_calls:
                tc_id = tc.id
                fn_name = tc.function.name
                raw_args = tc.function.arguments or "{}"

                try:
                    args = (
                        json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    )
                except Exception:
                    args = {}

                try:
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


if __name__ == "__main__":
    agent = Agent(
        session_id="axxxx",
        name="test",
        system_prompt="你是一个天气和文件管理助手。",
        llm=DeepSeek(model="deepseek-chat"),
        tools=[WeatherTool(), FileTool()],
        memory=Memory(),
    )
    agent.run("查询温度和湿度，并将结果保存到当前目录下的report.md文件中")
