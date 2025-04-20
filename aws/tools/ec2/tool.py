import subprocess
from typing import Any
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool
from .prompt import (
    PROMPT_CREATE_INSTANCE,
    PROMPT_TERMINATE_INSTANCE,
    PROMPT_MODIFY_INSTANCE,
)


class CreateEC2InstanceTool(BaseTool):
    """Tool to create EC2 instances via AWS CLI using LLM-generated commands."""

    name = "create_ec2_instance"
    description = (
        "Generate and run the AWS CLI command to create an EC2 instance based on a natural language query."
    )
    llm: BaseLanguageModel
    ec2_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_CREATE_INSTANCE.format(query=query)).strip()
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


class TerminateEC2InstanceTool(BaseTool):
    """Tool to terminate EC2 instances via AWS CLI using LLM-generated commands."""

    name = "terminate_ec2_instance"
    description = (
        "Generate and run the AWS CLI command to terminate EC2 instances based on a natural language query."
    )
    llm: BaseLanguageModel
    ec2_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_TERMINATE_INSTANCE.format(query=query)).strip()
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


class ModifyEC2InstancesTool(BaseTool):
    """Tool to modify EC2 instance attributes via AWS CLI using LLM-generated commands."""

    name = "modify_ec2_instances"
    description = (
        "Generate and run the AWS CLI command to modify EC2 instance attributes (e.g., change instance type) based on a natural language query."
    )
    llm: BaseLanguageModel
    ec2_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_MODIFY_INSTANCE.format(query=query)).strip()
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
