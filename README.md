# Agent 教程

学习 Agent 的教程、实现和记录（包含代码）

---

# RoadMap
add more advanced features tutorials later, including:
- [ ] Multi-Agents
- [ ] Todo Lists and Planning
- [ ] MCP, Skills and more
- [ ] Reflection and A2A, A2UI , etc.
- [ ] Advanced Memory Management
- [ ] Tool orchestration (routing, retries, fallbacks)
- [ ] Tool caching and idempotency
- [ ] Safety and guardrails
- [ ] Evaluation and testing (golden prompts, regression)
- [ ] Observability (logging, tracing, cost/latency)
- [ ] Context management (trim, summarize, chunk)
- [ ]RAG / Knowledge base (retrieval, citations)
- [ ]Prompting patterns (router, planner-executor)
- [ ] Streaming and UI
- [ ] Deployment and cost control (rate limit, model routing)
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

## 基础篇

| 文档 | 内容 |
|------|------|
| [01-miniagent](./docs/01-miniagent.md) | Agent 核心概念：LLM、Toolkit、Memory、Agent 的关系与实现 |
| [02-file&bash](./docs/02-file&bash.md) | FileTool：文件读写、命令执行、安全机制 |
| [03-todolist](./docs/03-todolist.md) | TodoList：任务规划与进度追踪 |
| [04-subagent](./docs/04-subagent.md) | SubAgentTool：子代理与多代理协作 |
| [05-skills](./docs/05-skills.md) | SkillTool：技能模块化与领域知识注入 |





References + Learning Resources:
DOCS:
[HelloAgents](https://github.com/jjyaoao/HelloAgents)
[learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)
[Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
[agno](https://docs.agno.com/)

VIDEOS:
[马克的技术工作坊](https://space.bilibili.com/1815948385)
