from .toolkit import Toolkit
import os


class FileTool(Toolkit):
    def __init__(self, work_dir: str = "."):
        self.work_dir = os.path.abspath(work_dir)
        super().__init__(
            name="FileTool",
            tools=[self.create_file, self.list_files],
        )

    def create_file(self, filename: str, content: str):
        """
        创建一个Markdown文件并写入初始内容

        Args:
            filename (str): 文件名
            content (str): 文件内容
        Returns:
            str: 创建文件的结果信息
        """
        with open(filename, "w") as f:
            f.write(content)
        return f"File '{filename}' created successfully and content written."

    def list_files(self, dir: str):
        """
        列出指定目录下的所有文件和文件夹

        Args:
            dir (str): 目录路径
        Returns:
            list[str]: 目录下的文件和文件夹列表
        """
        return os.listdir(dir)  # 当前目录
