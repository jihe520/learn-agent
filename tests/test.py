from pathlib import Path
from icecream import ic


from learn_agent.tool.file_tool import FileTool

file_tool = FileTool(Path.cwd() / "work_dir")
ic(file_tool.work_dir)
