import subprocess
from typing import Any
import json
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool
from .prompt import (
    PROMPT_PULL_IMAGE,
    PROMPT_BUILD_IMAGE,
    PROMPT_REMOVE_IMAGE,
    PROMPT_TAG_IMAGE,
    PROMPT_PUSH_IMAGE,
)


class PullImageTool(BaseTool):
    """Tool to pull Docker images via Docker CLI using LLM-generated commands."""
    
    name = "pull_docker_image"
    description = (
        "Generate and run the Docker command to pull an image from a registry based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_PULL_IMAGE.format(query=query)).strip()
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
                return f"Image pulled successfully: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class BuildImageTool(BaseTool):
    """Tool to build Docker images via Docker CLI using LLM-generated commands."""
    
    name = "build_docker_image"
    description = (
        "Generate and run the Docker command to build an image from a Dockerfile based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_BUILD_IMAGE.format(query=query)).strip()
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
                return f"Image built successfully: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class RemoveImageTool(BaseTool):
    """Tool to remove Docker images via Docker CLI using LLM-generated commands."""
    
    name = "remove_docker_image"
    description = (
        "Generate and run the Docker command to remove one or more images based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_REMOVE_IMAGE.format(query=query)).strip()
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
                return f"Image(s) removed: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class TagImageTool(BaseTool):
    """Tool to tag Docker images via Docker CLI using LLM-generated commands."""
    
    name = "tag_docker_image"
    description = (
        "Generate and run the Docker command to create a tag for an image based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_TAG_IMAGE.format(query=query)).strip()
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
                return "Image tagged successfully"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class PushImageTool(BaseTool):
    """Tool to push Docker images via Docker CLI using LLM-generated commands."""
    
    name = "push_docker_image"
    description = (
        "Generate and run the Docker command to push an image to a registry based on a natural language query."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_PUSH_IMAGE.format(query=query)).strip()
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
                return f"Image pushed successfully: {result.stdout}"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"


class ListImagesTool(BaseTool):
    """Tool to list Docker images."""
    
    name = "list_docker_images"
    description = (
        "List Docker images. "
        'Input should be a json string with one key: "all". '
        '"all" is a boolean value to indicate whether to list all images or just non-intermediate ones.'
    )

    def _run(self, text: str) -> str:
        input_data = json.loads(text)
        all_images = input_data.get("all", False)
        
        cmd = "docker images"
        if all_images:
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


class InspectImageTool(BaseTool):
    """Tool to inspect Docker images."""
    
    name = "inspect_docker_image"
    description = (
        "Inspect a Docker image to get detailed information about it. "
        'Input should be a string with the image ID or name.'
    )

    def _run(self, image_id: str) -> str:
        cmd = f"docker image inspect {image_id}"
            
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