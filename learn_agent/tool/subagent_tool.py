from learn_agent.tool.toolkit import Toolkit
from pydantic import BaseModel
from learn_agent.memory import Memory
from learn_agent.llm import DeepSeek
import time


# TODO: use pydantic model
class task(BaseModel):
    description: str
    prompt: str
    agent_type: dict


class SubAgentTool(Toolkit):
    def __init__(self, agent_type: dict, work_dir: str = "."):
        self.agent_type = agent_type
        self.work_dir = work_dir
        super().__init__(
            name="SubAgentTool",
            tools=[self.delegate_task],
        )

        """
        Execute a subagent task with isolated context.

        This is the core of the subagent mechanism:

        1. Create isolated message history (KEY: no parent context!)
        2. Use agent-specific system prompt
        3. Filter available tools based on agent type
        4. Run the same query loop as main agent
        5. Return ONLY the final text (not intermediate details)

        The parent agent sees just the summary, keeping its context clean.

        Progress Display:
        ----------------
        While running, we show:
          [explore] find auth files ... 5 tools, 3.2s

        This gives visibility without polluting the main conversation.
        """

    def delegate_task(self, description: str, prompt: str, agent_type: str) -> str:
        """
         Spawn a subagent for a focused subtask.

        Subagents run in ISOLATED context - they don't see parent's history.
        Use this to keep the main conversation clean.


        Example uses:
        - Task(explore): "Find all files using the auth module"
        - Task(plan): "Design a migration strategy for the database"
        - Task(code): "Implement the user registration form"
        """
        if agent_type not in self.agent_type:
            return f"Unknown agent type: {agent_type}"

        # process tracking
        print(f"[subagent:{agent_type}] starting task: {description}")
        start_time = time.time()

        config = self.agent_type[agent_type]
        # TODO: filter tools
        from learn_agent.agent.claude_code_agent import ClaudeCodeAgent

        sub_system_prompt = f"""you are a {agent_type} subagent. at {self.work_dir}
            {config["system_prompt"]}
        """
        sub_agent = ClaudeCodeAgent(
            session_id="subagent_session",
            name=f"subagent_{agent_type}",
            system_prompt=sub_system_prompt,
            llm=DeepSeek(model="deepseek-chat"),
            tools=[],
            memory=Memory(),
        )
        res = sub_agent.run(prompt)

        end_time = time.time()
        duration = end_time - start_time
        print(
            f"[subagent:{agent_type}] completed task: {description} in {duration:.2f}s"
        )
        return res

    def get_agent_descriptions(self) -> str:
        return "\n".join(
            f"- {name}: {config['description']}"
            for name, config in self.agent_type.items()
        )
