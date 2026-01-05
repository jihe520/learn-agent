# https://github.com/shareAI-lab/learn-claude-code/blob/main/v0_bash_agent.py
from learn_agent.tool.todo_tool import Todo
import sys
from icecream import ic
from learn_agent.agent import Agent
from learn_agent.llm import DeepSeek
from learn_agent.memory import Memory
from learn_agent.tool.file_tool import FileTool
import os

SYSTEM = f"""You are a coding agent at {os.getcwd()}.

Loop: think briefly -> use tools -> report results.

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

# TODO: todo list
# =============================================================================
# System Reminders - Soft prompts to encourage todo usage
# =============================================================================

# Shown at the start of conversation
INITIAL_REMINDER = "<reminder>Use TodoWrite for multi-step tasks.</reminder>"

# Shown if model hasn't updated todos in a while
NAG_REMINDER = (
    "<reminder>10+ turns without todo update. Please update todos.</reminder>"
)


# TODO : repl
# =============================================================================
# Main REPL
# =============================================================================


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # subagent mode
        ic("Running subagent with task:", sys.argv[1])
    else:
        agent = Agent(
            session_id="axxxx",
            name="test",
            system_prompt=SYSTEM,
            llm=DeepSeek(model="deepseek-chat"),
            tools=[FileTool(), Todo()],
            memory=Memory(),
        )
        res = agent.run("你好")
        ic(res)
