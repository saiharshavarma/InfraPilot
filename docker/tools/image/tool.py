import subprocess
from typing import Any
import json
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool
from tools.base.tools import RequireApprovalTool
from .prompt import (
    PROMPT_PULL_IMAGE,
    PROMPT_REMOVE_IMAGE,
    PROMPT_TAG_IMAGE,
    PROMPT_PUSH_IMAGE,
)
import os
import tempfile


class PullImageTool(BaseTool):
    """Tool to pull Docker images via Docker CLI using LLM-generated commands."""

    name = "pull_docker_image"
    description = "Generate and run the Docker command to pull an image from a registry based on a natural language query."
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


class BuildImageTool(RequireApprovalTool):
    """Tool to build Docker images from a GitHub repository."""

    name = "build_docker_image"
    description = (
        "Build a Docker image from a GitHub repository URL. "
        "Input should be a json string with at least a 'repo_url' key. "
        "Optional keys include 'image_name', 'tag', and 'dockerfile_path'."
    )
    llm: BaseLanguageModel

    def _run(self, text: str) -> str:
        import json

        try:
            input_data = json.loads(text)
            repo_url = input_data.get("repo_url")
            image_name = input_data.get("image_name", "")
            tag = input_data.get("tag", "latest")
            dockerfile_path = input_data.get("dockerfile_path", "Dockerfile")

            if not repo_url:
                return "Error: GitHub repository URL is required"

            # Default image name based on repo if not provided
            if not image_name:
                repo_parts = repo_url.rstrip("/").split("/")
                if len(repo_parts) > 1:
                    image_name = repo_parts[-1]
                else:
                    return "Error: Could not determine image name from repo URL. Please provide an image_name."

            # Create a temporary directory for cloning
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clone the repository
                clone_cmd = f"git clone {repo_url} {temp_dir}"
                clone_result = subprocess.run(
                    clone_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if clone_result.returncode != 0:
                    return f"Error cloning repository: {clone_result.stderr}"

                # Check if Dockerfile exists
                dockerfile_fullpath = os.path.join(temp_dir, dockerfile_path)
                if not os.path.exists(dockerfile_fullpath):
                    return f"Error: Dockerfile not found at {dockerfile_path} in the repository"

                # Build the Docker image
                build_cmd = f"docker build -t {image_name}:{tag} -f {dockerfile_fullpath} {temp_dir}"
                build_result = subprocess.run(
                    build_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if build_result.returncode != 0:
                    return (
                        f"Error building Docker image: {build_result.stderr}"
                    )

                return f"Successfully built Docker image {image_name}:{tag} from {repo_url}"

        except json.JSONDecodeError:
            return "Error: Input is not valid JSON"
        except Exception as e:
            return f"Exception: {e}"


class RemoveImageTool(BaseTool):
    """Tool to remove Docker images via Docker CLI using LLM-generated commands."""

    name = "remove_docker_image"
    description = "Generate and run the Docker command to remove one or more images based on a natural language query."
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
    description = "Generate and run the Docker command to create a tag for an image based on a natural language query."
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
    description = "Generate and run the Docker command to push an image to a registry based on a natural language query."
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        raw = self.llm.predict(PROMPT_PUSH_IMAGE.format(query=query)).strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])
        cmd = raw.strip()

        try:
            # Extract image name from the push command for tagging
            # Assuming standard format: docker push IMAGE_NAME
            push_parts = cmd.split()
            if (
                len(push_parts) >= 3
                and push_parts[0] == "docker"
                and push_parts[1] == "push"
            ):
                image_name = push_parts[2]

                # Tag the image before pushing (if username exists in environment)
                username = os.environ.get("DOCKER_USERNAME")
                if username:
                    # Create tag command
                    source_image = image_name
                    target_image = f"{username}/{image_name.split('/')[-1]}"
                    tag_cmd = f"docker tag {source_image} {target_image}"

                    # Run tag command
                    tag_result = subprocess.run(
                        tag_cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if tag_result.returncode != 0:
                        return f"Error tagging image: {tag_result.stderr}"

                    # Update the push command to use tagged image
                    cmd = f"docker push {target_image}"

            # Execute the push command
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
        "Input should be a string with the image ID or name."
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
