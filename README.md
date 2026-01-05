# Agent 教程

学习 Agent 的教程、实现和记录（包含代码）

---

# RoadMap
add more advanced features tutorials later, including:
- Multi-Agents
- Todo Lists and Planning
- MCP, Skills and more
- Reflection and A2A, A2UI , etc.
- Advanced Memory Management
- Tool orchestration (routing, retries, fallbacks)
- Tool caching and idempotency
- Safety and guardrails
- Evaluation and testing (golden prompts, regression)
- Observability (logging, tracing, cost/latency)
- Context management (trim, summarize, chunk)
- RAG / Knowledge base (retrieval, citations)
- Prompting patterns (router, planner-executor)
- Streaming and UI
- Deployment and cost control (rate limit, model routing)
...

This project just for learning purpose.

---

# 教程

安装,并运行
```
uv sync
# 修改.env.example为.env，填写 DeepSeek API Key
uv run main.py
```

[01-miniagent](./docs/01-miniagent.md):
对于 Agent 初学者 的最小化教程
1. 以一个最小 Agent 实现为例子
2. 一个 Python 文件，大约300 行代码



References + Learning Resources:
[HelloAgents](https://github.com/jjyaoao/HelloAgents)
[learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)
[Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)