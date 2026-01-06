from icecream import ic
from learn_agent.agent.agent import Agent
from learn_agent.llm import DeepSeek
from learn_agent.memory import Memory
from learn_agent.tool.file_tool import FileTool
from learn_agent.tool.weather_tool import WeatherTool


if __name__ == "__main__":
    agent = Agent(
        session_id="axxxx",
        name="test",
        system_prompt="你是一个天气和文件管理助手。",
        llm=DeepSeek(model="deepseek-chat"),
        tools=[WeatherTool(), FileTool()],
        memory=Memory(),
    )
    res = agent.run("你好")
    ic(res)
