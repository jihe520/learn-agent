# https://github.com/shareAI-lab/learn-claude-code/blob/main/v0_bash_agent.py
from operator import sub
import sys
from icecream import ic
from learn_agent.agent.claude_code_agent import ClaudeCodeAgent
from learn_agent.llm import DeepSeek
from learn_agent.memory import Memory
from learn_agent.tool.file_tool import FileTool
from learn_agent.tool.todo_tool import TodoTool
from learn_agent.tool.subagent_tool import SubAgentTool
from learn_agent.tool.skill_tool import SkillTool
from pathlib import Path
import os


AGENT_TYPES = {
    # Explore: Read-only agent for searching and analyzing
    # Cannot modify files - safe for broad exploration
    "explore": {
        "description": "Read-only agent for exploring code, finding files, searching",
        "tools": FileTool(include_tools=["bash", "read_file"]),  # No write access
        "system_prompt": "You are an exploration agent. Search and analyze, but never modify files. Return a concise summary.",
    },
    # Code: Full-powered agent for implementation
    # Has all tools - use for actual coding work
    "code": {
        "description": "Full agent for implementing features and fixing bugs",
        "tools": [FileTool()],  # All tools
        "system_prompt": "You are a coding agent. Implement the requested changes efficiently.",
    },
    # Plan: Analysis agent for design work
    # Read-only, focused on producing plans and strategies
    "plan": {
        "description": "Planning agent for designing implementation strategies",
        "tools": [FileTool(include_tools=["bash", "read_file"])],  # Read-only
        "system_prompt": "You are a planning agent. Analyze the codebase and output a numbered implementation plan. Do NOT make changes.",
    },
}

if __name__ == "__main__":
    print("Claude Code Agent")
    print("Type 'exit' to quit.")
    work_dir = Path.cwd() / "work_dir"
    file_tool = FileTool(work_dir=work_dir)
    todo_tool = TodoTool()
    skill_tool = SkillTool(Path("skills"))
    subagent_tool = SubAgentTool(
        AGENT_TYPES,
        available_toolkits=[file_tool, todo_tool, skill_tool],
        work_dir=work_dir,
    )
    SYSTEM = f"""You are a coding agent at {work_dir.absolute()}.

Loop: think briefly -> use tools -> report results.


**Skills available** (invoke with Skill tool when task matches):
{skill_tool.get_descriptions()}

**Subagents available** (invoke with Task tool for focused subtasks):
{subagent_tool.get_agent_descriptions()}

Rules:
- Prefer tools over prose. Act first, explain briefly after.
- Read files: cat, grep, find, rg, ls, head, tail
- Write files: echo '...' > file, sed -i, or cat << 'EOF' > file
- Subagent: For complex subtasks, spawn a subagent to keep context clean:
  python claudecode.py "explore src/ and summarize the architecture"
- Never invent file paths. Use ls/find first if unsure.
- Make minimal changes. Don't over-engineer.
- After finishing, summarize what changed.

- Use Todo to track multi-step tasks
- Mark tasks in_progress before starting, completed when done
- Prefer tools over prose. Act, don't just explain.
- After finishing, summarize what changed

When to use subagent:
- Task requires reading many files (isolate the exploration)
- Task is independent and self-contained
- You want to avoid polluting current conversation with intermediate details

The subagent runs in isolation and returns only its final summary."""
    while True:
        try:
            user_input = input("User: ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting...")
            break

        try:
            agent = ClaudeCodeAgent(
                session_id="axxxx",
                name="test",
                system_prompt=SYSTEM,
                llm=DeepSeek(model="deepseek-chat"),
                tools=[
                    file_tool,
                    todo_tool,
                    subagent_tool,
                    skill_tool,
                ],
                memory=Memory(),
            )
            response = agent.run(user_input)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")
