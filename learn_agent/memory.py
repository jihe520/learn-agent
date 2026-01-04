# 简单的内存模块，保存对话上下文
class Memory:
    def __init__(self):
        self.messages: list[dict] = []

    def add_message(self, role: str, content: str | None = None, **extra):
        # messages 列表里保存对话上下文
        msg = {"role": role}
        if content is not None:  # 大模型返回的 tool 调用结果可能没有 content
            msg["content"] = content
        msg.update(extra)  # 再此还有可以优化超出max_tokens的情况
        self.messages.append(msg)

    def get_context(self) -> list[dict]:
        return self.messages  # 返回当前的对话上下文,每次请求都带上
