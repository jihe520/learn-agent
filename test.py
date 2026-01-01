import inspect
from icecream import ic
from main import function_to_tool_schema


def get_temperature(self, num: int | None = 2) -> list[dict[str, float]]:
    """
    获取几天的温度

    Args:
        num (int | None): 天数，默认2天
    Returns:
        list[dict[str, float]]: 日期和温度对应的列表
    """
    return [{"2024-01-01": 25.0}, {"2024-01-02": 26.5}]


# sig = inspect.signature(get_temperature)
# ic(sig.parameters.items())
# ic(inspect.getdoc(get_temperature))
# ic(function_to_tool_schema(get_temperature))
ic(get_temperature.__name__)
