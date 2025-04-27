import subprocess
from typing import Any
import json
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool
from tools.base.tools import RequireApprovalTool
from .prompt import (
    PROMPT_RUN_CONTAINER,
    PROMPT_STOP_CONTAINER,
    PROMPT_REMOVE_CONTAINER,
    PROMPT_EXEC_CONTAINER,
    PROMPT_LOGS_CONTAINER,
)


class RunContainerTool(RequireApprovalTool):
    """Tool to run a Docker container via Docker CLI using LLM-generated commands."""

    name = "run_docker_container"
    description = "Generate and run the Docker command to create and run a container based on a natural language query."
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(
            PROMPT_RUN_CONTAINER.format(query=query)
        ).strip()
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
                return f"Container started successfully: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class StopContainerTool(BaseTool):
    """Tool to stop Docker containers via Docker CLI using LLM-generated commands."""

    name = "stop_docker_container"
    description = "Generate and run the Docker command to stop one or more running containers based on a natural language query."
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(
            PROMPT_STOP_CONTAINER.format(query=query)
        ).strip()
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
                return f"Container(s) stopped: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class RemoveContainerTool(BaseTool):
    """Tool to remove Docker containers via Docker CLI using LLM-generated commands."""

    name = "remove_docker_container"
    description = "Generate and run the Docker command to remove one or more containers based on a natural language query."
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(
            PROMPT_REMOVE_CONTAINER.format(query=query)
        ).strip()
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
                return f"Container(s) removed: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class ExecContainerTool(BaseTool):
    """Tool to execute commands in Docker containers via Docker CLI using LLM-generated commands."""

    name = "exec_docker_container"
    description = "Generate and run the Docker command to execute a command in a running container based on a natural language query."
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(
            PROMPT_EXEC_CONTAINER.format(query=query)
        ).strip()
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
                return result.stdout
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class LogsContainerTool(BaseTool):
    """Tool to get logs from Docker containers via Docker CLI using LLM-generated commands."""

    name = "logs_docker_container"
    description = "Generate and run the Docker command to fetch logs from a container based on a natural language query."
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(
            PROMPT_LOGS_CONTAINER.format(query=query)
        ).strip()
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
                return f"```\n{result.stdout}\n```"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class ListContainersTool(BaseTool):
    """Tool to list Docker containers."""

    name = "list_docker_containers"
    description = (
        "List Docker containers. "
        'Input should be a json string with one key: "all". '
        '"all" is a boolean value to indicate whether to list all containers or just running ones.'
    )

    def _run(self, text: str) -> str:
        input_data = json.loads(text)
        all_containers = input_data.get("all", False)

        cmd = "docker ps"
        if all_containers:
            cmd += " -a"

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


class InspectContainerTool(BaseTool):
    """Tool to inspect Docker containers."""

    name = "inspect_docker_container"
    description = (
        "Inspect a Docker container to get detailed information about it. "
        "Input should be a string with the container ID or name."
    )

    def _run(self, container_id: str) -> str:
        cmd = f"docker inspect {container_id}"

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
