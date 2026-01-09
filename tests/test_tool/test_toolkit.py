"""测试 toolkit 参数描述解析功能"""

import pytest
from learn_agent.tool.toolkit import function_to_tool_schema, _parse_param_descriptions
from learn_agent.tool.file_tool import FileTool


def test_parse_param_descriptions():
    doc = """读取文件内容

    Args:
        path: 文件路径（绝对路径）
        encoding: 编码格式，默认 utf-8
    """
    result = _parse_param_descriptions(doc)
    assert result == {
        "path": "文件路径（绝对路径）",
        "encoding": "编码格式，默认 utf-8",
    }


def test_parse_empty_doc():
    assert _parse_param_descriptions("") == {}
    assert _parse_param_descriptions(None) == {}


def test_real_file_tool_schema():
    """用真实的 FileTool 函数测试 schema 生成"""
    file_tool = FileTool()

    # 测试 bash 函数
    schema = function_to_tool_schema(file_tool.bash)
    assert schema["function"]["name"] == "bash"
    props = schema["function"]["parameters"]["properties"]
    assert props["command"]["type"] == "string"
    assert props["command"]["description"] == "shell command to execute"

    # 测试 read_file 函数
    schema = function_to_tool_schema(file_tool.read_file)
    assert schema["function"]["name"] == "read_file"
    props = schema["function"]["parameters"]["properties"]
    assert props["path"]["description"] == "Path to the file to read."
    assert props["limit"]["description"] == "Optional"

    # 检查必填参数
    assert "path" in schema["function"]["parameters"]["required"]
    assert "limit" not in schema["function"]["parameters"]["required"]


def test_parse_multiline_descriptions():
    """测试多行参数描述解析"""
    doc = """下载文件到本地

    Args:
        url: 要下载的文件 URL 地址
            支持 http/https 协议
        path: 保存的文件路径
            必须是绝对路径
        overwrite: 是否覆盖已存在的文件
    """
    result = _parse_param_descriptions(doc)
    assert result == {
        "url": "要下载的文件 URL 地址 支持 http/https 协议",
        "path": "保存的文件路径 必须是绝对路径",
        "overwrite": "是否覆盖已存在的文件",
    }
