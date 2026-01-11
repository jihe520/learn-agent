from learn_agent.tool.cognee_tool import CogneeTool
from icecream import ic
from learn_agent.agent.agent import Agent
from learn_agent.llm import DeepSeek
from learn_agent.memory import Memory


if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting...")
            break

        try:
            agent = Agent(
                session_id="axxxx",
                name="test",
                system_prompt="你是一个本地用户助手，可以帮助用户处理本地工作。 Use remember() to store important details and recall() to retrieve past context.",
                llm=DeepSeek(model="deepseek-chat"),
                tools=[CogneeTool()],
                memory=Memory(),
            )
            response = agent.run(user_input)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")

# Session 1: Learn client preferences
# agent.run(
#     "Remember: Acme Corp requires 30-day payment terms and California arbitration."
# )

# Session 2: Use memory for analysis
# agent.run("Review this contract for Acme Corp: 60-day terms, New York jurisdiction.")
# # Agent calls recall() → flags mismatches with stored preferences
