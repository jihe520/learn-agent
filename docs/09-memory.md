# Memory - 记忆模块

本项目实现了两种记忆机制：**Memory 类**（对话上下文存储）和 **Mem0Tool**（长期记忆存储）。

## 1. Memory 类 - 对话上下文

用于存储对话历史，在 Agent 运行时保持上下文。

```python
from learn_agent.memory.memory import Memory

# 创建记忆存储
memory = Memory()

# 添加用户消息
memory.add("user", "Hello, my name is John")

# 添加助手回复
memory.add("assistant", "Hi John! Nice to meet you.")

# 获取所有消息
messages = memory.get_messages()
```

**源码：** [learn_agent/memory/memory.py](learn_agent/memory/memory.py)

## 2. Mem0Tool - 长期记忆存储

使用 [mem0](https://github.com/agno-agi/mem0) 实现跨会话的持久化记忆，支持语义搜索。

### 2.1 快速开始

```python
from learn_agent.tool.mem0_tool import Mem0Tool

# 初始化（指定 user_id 用于区分不同用户）
memory_tool = Mem0Tool(user_id="user_123")
```

### 2.2 可用方法

| 方法 | 描述 |
|------|------|
| `add_memory(content)` | 添加新记忆 |
| `search_memory(query)` | 语义搜索相关记忆 |
| `get_all_memories()` | 获取所有记忆 |
| `delete_memory(memory_id)` | 删除指定记忆 |

### 2.3 使用示例

```python
import asyncio
from learn_agent.tool.mem0_tool import Mem0Tool

async def main():
    memory_tool = Mem0Tool(user_id="demo_user")

    # 添加记忆
    memory_tool.add_memory("My name is John and I prefer dark mode")
    memory_tool.add_memory("I am allergic to peanuts and shellfish")

    # 搜索记忆
    results = memory_tool.search_memory("What are my food preferences?")
    print(results)

    # 获取所有记忆
    all_memories = memory_tool.get_all_memories()
    print(all_memories)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2.4 在 Agent 中使用

```python
from learn_agent.agent.agent import Agent
from learn_agent.tool.mem0_tool import Mem0Tool

agent = Agent(
    tools=[Mem0Tool(user_id="user_123")],
)

agent.run("Remember that I prefer vegetarian meals")
response = agent.run("What do I prefer to eat?")
```

## 3. 环境配置

需要在 `.env` 中配置 mem0 API key：

```bash
MEM0_API_KEY="your-api-key"
```

## 4. 记忆对比

| 特性 | Memory 类 | Mem0Tool |
|------|-----------|----------|
| 用途 | 对话上下文 | 长期记忆 |
| 持久化 | 会话内 | 跨会话 |
| 搜索 | 线性遍历 | 语义搜索 |
| 过期 | 会话结束清除 | 永久存储 |

## 5. 源码

- **Memory 类：** [learn_agent/memory/memory.py](learn_agent/memory/memory.py)
- **Mem0Tool：** [learn_agent/tool/mem0_tool.py](learn_agent/tool/mem0_tool.py)
- **示例：** [examples/mem0_example.py](../examples/mem0_example.py)
