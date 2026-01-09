from icecream import ic
from learn_agent.agent.agent import Agent
from learn_agent.llm import DeepSeek
from learn_agent.memory import Memory
from learn_agent.tool.weather_tool import WeatherTool
from learn_agent.tool.file_tool import FileTool
from learn_agent.tool.todo_tool import TodoTool
from pathlib import Path

if __name__ == "__main__":
    agent = Agent(
        session_id="axxxx",
        name="test",
        system_prompt="你是一个本地用户助手，可以帮助用户处理本地工作。",
        llm=DeepSeek(model="deepseek-chat"),
        tools=[WeatherTool(), FileTool(work_dir=Path.cwd() / "work_dir"), TodoTool()],
        memory=Memory(),
    )
    res = agent.run("查看下当前文件夹")
    ic(res)
