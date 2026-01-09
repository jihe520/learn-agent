from .toolkit import Toolkit


class WeatherTool(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(
            name="WeatherTool",
            tools=[self.get_temperature, self.get_humidity],
            **kwargs,
        )

    def get_temperature(self, num: int | None = 2) -> list[dict[str, float]]:
        """
        获取几天的温度

        Args:
            num (int | None): 天数，默认2天
        Returns:
            list[dict[str, float]]: 日期和温度对应的列表
        """
        return [{"2024-01-01": 25.0}, {"2024-01-02": 26.5}]  # 示例数据

    def get_humidity(self, num: int | None = 2) -> list[dict[str, float]]:
        """
        获取几天的湿度

        Args:
            num (int | None): 天数，默认2天
        Returns:
            list[dict[str, float]]: 日期和湿度对应的列表
        """
        return [{"2024-01-01": 60.0}, {"2024-01-02": 65.0}]  # 模拟数据
