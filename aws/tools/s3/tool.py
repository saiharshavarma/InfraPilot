import subprocess
from typing import Any
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool
from .prompt import (
    PROMPT_CREATE_BUCKET,
    PROMPT_LIST_BUCKETS,
    PROMPT_UPLOAD_OBJECT,
    PROMPT_DELETE_OBJECT,
)

class CreateS3BucketTool(BaseTool):
    name = "create_s3_bucket"
    description = "Generate and run AWS CLI command to create an S3 bucket based on a natural language query."
    llm: BaseLanguageModel
    s3_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_CREATE_BUCKET.format(query=query)).strip()
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

class ListS3BucketsTool(BaseTool):
    name = "list_s3_buckets"
    description = "Generate and run AWS CLI command to list S3 buckets based on a natural language query."
    llm: BaseLanguageModel
    s3_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_LIST_BUCKETS.format(query=query)).strip()
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

class UploadS3ObjectTool(BaseTool):
    name = "upload_s3_object"
    description = "Generate and run AWS CLI command to upload a file to S3 based on a natural language query."
    llm: BaseLanguageModel
    s3_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_UPLOAD_OBJECT.format(query=query)).strip()
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

class DeleteS3ObjectTool(BaseTool):
    name = "delete_s3_object"
    description = "Generate and run AWS CLI command to delete an object from S3 based on a natural language query."
    llm: BaseLanguageModel
    s3_client: Any

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_DELETE_OBJECT.format(query=query)).strip()
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