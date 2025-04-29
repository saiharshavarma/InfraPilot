import subprocess
from typing import Any
import json
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool
from tools.base.tools import RequireApprovalTool
from .prompt import (
    PROMPT_CREATE_VOLUME,
    PROMPT_REMOVE_VOLUME,
    PROMPT_INSPECT_VOLUME,
)


class CreateVolumeTool(BaseTool):
    """Tool to create Docker volumes via Docker CLI using LLM-generated commands."""
    
    name = "create_docker_volume"
    description = (
        "Generate and run the Docker command to create a volume based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_CREATE_VOLUME.format(query=query)).strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                return f"Volume created: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class RemoveVolumeTool(RequireApprovalTool):
    """Tool to remove Docker volumes via Docker CLI using LLM-generated commands."""
    
    name = "remove_docker_volume"
    description = (
        "Generate and run the Docker command to remove one or more volumes based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_REMOVE_VOLUME.format(query=query)).strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                return f"Volume(s) removed: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class InspectVolumeTool(BaseTool):
    """Tool to inspect Docker volumes via Docker CLI using LLM-generated commands."""
    
    name = "inspect_docker_volume"
    description = (
        "Generate and run the Docker command to inspect one or more volumes based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_INSPECT_VOLUME.format(query=query)).strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                # Parse the output as JSON for better formatting
                inspect_data = json.loads(result.stdout)
                # Return a formatted JSON string
                return json.dumps(inspect_data, indent=2)
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class ListVolumesTool(BaseTool):
    """Tool to list Docker volumes."""
    
    name = "list_docker_volumes"
    description = (
        "List Docker volumes. "
        'Input can be empty.'
    )

    def _run(self, text: str = "") -> str:
        cmd = "docker volume ls"
            
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                return f"```\n{result.stdout}\n```"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"