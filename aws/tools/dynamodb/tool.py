import subprocess
from typing import Any
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool
from .prompt import PROMPT_CREATE_TABLE, PROMPT_PUT_ITEM, PROMPT_GET_ITEM

class CreateDynamoDBTableTool(BaseTool):
    name = "create_dynamodb_table"
    description = "Generate and run AWS CLI command to create a DynamoDB table based on a natural language query."
    llm: BaseLanguageModel
    dynamodb_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_CREATE_TABLE.format(query=query)).strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return result.stdout
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"

class PutDynamoDBItemTool(BaseTool):
    name = "put_dynamodb_item"
    description = "Generate and run AWS CLI command to put an item into a DynamoDB table based on a natural language query."
    llm: BaseLanguageModel
    dynamodb_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_PUT_ITEM.format(query=query)).strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return result.stdout
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"

class GetDynamoDBItemTool(BaseTool):
    name = "get_dynamodb_item"
    description = "Generate and run AWS CLI command to get an item from a DynamoDB table based on a natural language query."
    llm: BaseLanguageModel
    dynamodb_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_GET_ITEM.format(query=query)).strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return result.stdout
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"
