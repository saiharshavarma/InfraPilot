# tool.py

import subprocess
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool

from .prompt import (
    PROMPT_GENERATE_CLOUDFORMATION_TEMPLATE,
    PROMPT_DEPLOY_CLOUDFORMATION_STACK,
)


class GenerateCloudFormationTemplateTool(BaseTool):
    """Tool to generate and save a CloudFormation YAML template from a natural language query."""

    name = "generate_cloudformation_template"
    description = (
        "Generate an AWS CloudFormation template in YAML based on a natural language query "
        "and save it to template.yaml."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(
            PROMPT_GENERATE_CLOUDFORMATION_TEMPLATE.format(query=query)
        ).strip()
        # strip markdown code fences if present
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        filename = "template.yaml"
        try:
            with open(filename, "w") as f:
                f.write(raw)
            return f"CloudFormation template written to {filename}"
        except Exception as e:
            return f"Error writing template: {e}"


class DeployCloudFormationStackTool(BaseTool):
    """Tool to deploy a CloudFormation stack via AWS CLI using an LLM‐generated command."""

    name = "deploy_cloudformation_stack"
    description = (
        "Generate and run an AWS CLI command to deploy a CloudFormation stack "
        "from template.yaml based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(
            PROMPT_DEPLOY_CLOUDFORMATION_STACK.format(query=query)
        ).strip()
        # strip markdown code fences if present
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()
        try:
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                return result.stdout
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"
