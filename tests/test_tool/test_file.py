import pytest
from learn_agent.tool.file_tool import FileTool
from icecream import ic
from pathlib import Path


@pytest.fixture
def file_tool():
    return FileTool(work_dir=Path.cwd() / "work_dir")


def test_bash(file_tool: FileTool):
    output = file_tool.bash("echo Hello, World!")
    file_list = file_tool.bash("ls")
    ic(output)
    ic(file_list)
    assert "Hello, World!" in output
    assert "test.md" in file_list
