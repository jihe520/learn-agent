from pathlib import Path
from .toolkit import Toolkit
import os


# https://github.com/jjyaoao/HelloAgents/blob/main/hello_agents/tools/builtin/terminal_tool.py
class FileTool(Toolkit):
    def __init__(self, work_dir: Path = Path.cwd()):
        self.work_dir = os.path.abspath(work_dir)
        super().__init__(
            name="FileTool",
            tools=[self.bash, self.read_file, self.write_file, self.edit_file],
        )

    def _safe_path(self, p: str) -> Path:
        # 防止路径穿越攻击
        path = (Path(self.work_dir) / p).resolve()
        if not path.is_relative_to(Path(self.work_dir).resolve()):
            raise ValueError("Unsafe path detected.")
        return path

    def bash(self, command: str):
        """
        execute shell command. common patterns:
        - Read: cat/head/tail,grep/find/rg/ls,wc -l
        - Write: echo,>,>>,tee
        """
        import subprocess

        DANGER_COMMANDS = ["rm -rf /", "sudo", "shutdown", "reboot"]
        if any(d in command for d in DANGER_COMMANDS):
            return "ERROR: Dangerous command detected. Aborting."

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.work_dir,
                timeout=300,
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "Command timed out."

        return output[:50000]

    def read_file(self, path: str, limit: int | None = None) -> str:
        """
        Read file contents with optional line limit.

        For large files, use limit to read just the first N lines.
        Output truncated to 50KB to prevent context overflow.
        """
        try:
            text = self._safe_path(path).read_text()
            lines = text.splitlines()

            if limit and limit < len(lines):
                lines = lines[:limit]
                lines.append(f"... ({len(text.splitlines()) - limit} more lines)")

            return "\n".join(lines)[:50000]

        except Exception as e:
            return f"Error: {e}"

    def write_file(self, path: str, content: str) -> str:
        """
        Write content to file, creating parent directories if needed.

        This is for complete file creation/overwrite.
        For partial edits, use edit_file instead.
        """
        try:
            fp = self._safe_path(path)
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content)
            return f"Wrote {len(content)} bytes to {path}"

        except Exception as e:
            return f"Error: {e}"

    def edit_file(self, path: str, old_text: str, new_text: str) -> str:
        """
        Replace exact text in a file (surgical edit).

        Uses exact string matching - the old_text must appear verbatim.
        Only replaces the first occurrence to prevent accidental mass changes.
        """
        try:
            fp = self._safe_path(path)
            content = fp.read_text()

            if old_text not in content:
                return f"Error: Text not found in {path}"

            # Replace only first occurrence for safety
            new_content = content.replace(old_text, new_text, 1)
            fp.write_text(new_content)
            return f"Edited {path}"

        except Exception as e:
            return f"Error: {e}"
