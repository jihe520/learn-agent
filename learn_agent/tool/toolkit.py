from typing import Any, Callable
import inspect


def _py_type_to_json_type(t: Any) -> str:
    # 极简映射：够用即可（你后面可以扩展）对应 OpenAI tools schema 里的数据类型
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
    # 从函数签名里拿到参数名、默认值、注解
    sig = inspect.signature(fn)
    props: dict[str, Any] = {}
    required: list[str] = []

    for name, p in sig.parameters.items():
        if name == "self":
            continue
        ann = p.annotation if p.annotation is not inspect._empty else str
        # 处理 Optional[...] / Union[...]：这里只做最小化映射
        json_type = _py_type_to_json_type(
            ann if ann in (int, float, bool, str) else str
        )
        props[name] = {"type": json_type}

        if p.default is inspect._empty:
            # 没有默认值的参数视为必填
            required.append(name)

    doc = inspect.getdoc(fn) or ""  # 函数的 docstring
    fn_name = getattr(fn, "__name__", fn.__class__.__name__)  # 函数名
    desc = (
        doc.strip().split("\n\n")[0] if doc.strip() else f"Call {fn_name}"
    )  # 简单取 docstring 第一段作为描述

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


# 通过继承 Toolkit 来实现自己定制的具体的工具包，可以添加自己的参数和方法


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
        # 把工具函数统一转换为 OpenAI tools schema
        return [function_to_tool_schema(fn) for fn in self._tools.values()]

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def call(self, tool_name: str, **kwargs) -> Any:
        # 调用具体的工具函数
        if not self.has(tool_name):
            raise ValueError(f"Tool {tool_name} not found in toolkit {self.name}")
        fn = self._tools[tool_name]
        return fn(**kwargs)
