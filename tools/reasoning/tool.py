from config import config

from langchain.tools.base import BaseTool


class ShowReasoningTool(BaseTool):
    """Tool that show infrapilot reasoning output."""

    name = "show_reasoning_output"
    description = "Show infrapilot reasoning output."

    def _run(self, query: str) -> str:
        config.set_show_reasoning(True)
        return "succeed."


class HideReasoningTool(BaseTool):
    """Tool that hide infrapilot reasoning output."""

    name = "hide_reasoning_output"
    description = "Hide infrapilot reasoning output."

    def _run(self, query: str) -> str:
        config.set_show_reasoning(False)
        return "succeed."
