from typing import Any, Callable
import inspect


def _parse_param_descriptions(doc: str | None) -> dict[str, str]:
    """从 Google 风格 docstring 解析参数描述，支持多行描述和类型注解"""
    if not doc:
        return {}

    result = {}
    lines = doc.split("\n")
    in_args = False
    current_param = None
    current_desc_lines: list[str] = []

    for line in lines:
        stripped = line.strip()

        # 检测 Args 区域开始
        if stripped.lower().startswith("args:"):
            in_args = True
            continue

        # 检测其他区域开始，结束 Args 解析
        if stripped.lower().startswith(
            ("returns:", "examples:", "notes:", "raises:", "attributes:")
        ):
            if current_param:
                result[current_param] = " ".join(current_desc_lines)
            in_args = False
            current_param = None
            current_desc_lines = []
            continue

        # 在 Args 区域内
        if in_args:
            content = stripped.lstrip("-").strip()
            is_param_line = ":" in content and not content.split(":")[0].startswith(
                "http"
            )

            if is_param_line:
                if current_param:
                    result[current_param] = " ".join(current_desc_lines)

                param_part = content.split(":")[0].strip()
                param_desc = content.split(":", 1)[1].strip()

                # 处理 "param (type)" 格式，提取参数名
                if "(" in param_part:
                    param_name = param_part.split("(")[0].strip()
                else:
                    param_name = param_part

                current_param = param_name
                current_desc_lines = [param_desc] if param_desc else []
            elif current_param and stripped:
                current_desc_lines.append(stripped)

    if current_param:
        result[current_param] = " ".join(current_desc_lines)

    return result


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
    - description 用 docstring
    """
    doc = inspect.getdoc(fn) or ""
    param_descs = _parse_param_descriptions(doc)

    sig = inspect.signature(fn)
    props: dict[str, Any] = {}
    required: list[str] = []

    for name, p in sig.parameters.items():
        if name == "self":
            continue
        ann = p.annotation if p.annotation is not inspect._empty else str
        json_type = _py_type_to_json_type(
            ann if ann in (int, float, bool, str) else str
        )
        props[name] = {"type": json_type, "description": param_descs.get(name, "")}

        if p.default is inspect._empty:
            required.append(name)

    fn_name = getattr(fn, "__name__", fn.__class__.__name__)

    return {
        "type": "function",
        "function": {
            "name": fn_name,
            "description": doc,
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
        **kwargs,
    ):
        self.name = name or self.__class__.__name__
        self._tools: dict[str, Callable] = {}
        include_tools = kwargs.get("include_tools")
        include_set = set(include_tools) if include_tools else None
        if tools:
            for fn in tools:
                fn_name = getattr(fn, "__name__", fn.__class__.__name__)
                if include_set is None or fn_name in include_set:
                    self._tools[fn_name] = fn

    @staticmethod
    def _normalize_tool_spec(tool_spec) -> tuple[set[str], set[str]]:
        if tool_spec is None or tool_spec == "*":
            return {"*"}, set()
        if isinstance(tool_spec, dict):
            include = set(tool_spec.get("include") or [])
            exclude = set(tool_spec.get("exclude") or [])
            return include, exclude
        if isinstance(tool_spec, (list, tuple, set)):
            return set(tool_spec), set()
        if isinstance(tool_spec, str):
            return {tool_spec}, set()
        return {"*"}, set()

    def select_tools(self, tool_spec=None) -> "Toolkit":
        include, exclude = self._normalize_tool_spec(tool_spec)
        if include and "*" in include and not exclude:
            return self
        if include and "*" not in include:
            selected = {name: fn for name, fn in self._tools.items() if name in include}
        else:
            selected = dict(self._tools)
        if exclude:
            selected = {
                name: fn for name, fn in selected.items() if name not in exclude
            }
        if selected is self._tools:
            return self
        return Toolkit(name=self.name, tools=list(selected.values()))

    def list_tools_schemas(self) -> list[dict]:
        # 把工具函数统一转换为 OpenAI tools schema
        return [function_to_tool_schema(fn) for fn in self._tools.values()]

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def call(self, tool_name: str, **kwargs) -> Any:
        print(f"Calling tool {tool_name} with args {kwargs}")
        # 调用具体的工具函数
        if not self.has(tool_name):
            raise ValueError(f"Tool {tool_name} not found in toolkit {self.name}")
        fn = self._tools[tool_name]
        return fn(**kwargs)
