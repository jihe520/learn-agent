from icecream import ic
from openai import OpenAI
import os
from dotenv import load_dotenv

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

        # 初始化 OpenAI 客户端，后续所有调用都走这个 client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat(self, messages: list[dict], tools: list[dict] | None = None):
        # 组装请求参数，按需加入可选项
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

        # 发起一次非流式对话请求，非流式更适合学习和调试
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
