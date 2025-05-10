import subprocess
import re
import yaml
import random
import string
import os
import time
from collections import OrderedDict
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool

from .prompt import (
    PROMPT_GENERATE_CLOUDFORMATION_TEMPLATE,
    PROMPT_DEPLOY_CLOUDFORMATION_STACK,
)

class GenerateCloudFormationTemplateTool(BaseTool):
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

        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1])

        try:
            parsed = yaml.safe_load(raw)
            if not isinstance(parsed, dict):
                return "Error: Generated YAML does not contain a valid CloudFormation template structure"
            if "Resources" not in parsed:
                parsed["Resources"] = {}
        except Exception as e:
            return f"Error parsing generated YAML: {e}"

        resources = parsed.get("Resources", {})
        new_resources = {}

        for res_name, res in resources.items():
            if not isinstance(res, dict):
                continue
            res_type = res.get("Type")
            if not res_type:
                continue
            props = res.get("Properties", {}) or {}
            if res_type == "AWS::S3::Bucket":
                suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                fixed_name = f"cf-bucket-zchen-{res_name.lower()}-{suffix}"
                props["BucketName"] = fixed_name.lower()
            if props == {}:
                props = None
            new_entry = OrderedDict()
            new_entry["Type"] = res_type
            if props is not None:
                new_entry["Properties"] = props
            new_resources[res_name] = dict(new_entry)

        parsed["Resources"] = new_resources

        try:
            with open("template.yaml", "w") as f:
                yaml.dump(parsed, f, default_flow_style=False, sort_keys=False)
            return "CloudFormation template written to template.yaml"
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
        import subprocess
        import json
        import time

        # First check if AWS CLI connection is working
        aws_check_cmd = "aws sts get-caller-identity"
        aws_check_result = subprocess.run(
            aws_check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        # Check if AWS CLI connection is properly established
        if aws_check_result.returncode != 0:
            return f"Error: AWS CLI connection failed. Please check your AWS credentials and network connection.\nError details: {aws_check_result.stderr}"

        raw = self.llm.predict(
            PROMPT_DEPLOY_CLOUDFORMATION_STACK.format(query=query)
        ).strip()

        # Clear markdown formatting
        lines = raw.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
            if lines and lines[-1].strip().endswith("```"):
                lines = lines[:-1]
        cmd = "\n".join(lines).strip()

        print("Generated AWS CLI command:", cmd)
        
        # Extract stack-name parameter from command
        stack_name_match = re.search(r'--stack-name\s+(\S+)', cmd)
        if not stack_name_match:
            return "Error: Could not find stack name in the command."
        
        stack_name = stack_name_match.group(1)
        
        # Extract region parameter if present
        region_match = re.search(r'--region\s+(\S+)', cmd)
        region_param = f"--region {region_match.group(1)}" if region_match else ""

        try:
            # Execute deployment command
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Check deployment command execution results
            if result.returncode != 0:
                # Command failed, return error message
                return f"Error during deployment:\n{result.stderr}"
            
            # Command executed successfully, but we need to verify if the stack was actually created/updated
            if "No changes to deploy" in result.stdout or "No changes to deploy" in result.stderr:
                return "Stack is already up-to-date. No changes were made."
                
            # Verify stack status
            max_attempts = 5
            attempts = 0
            
            while attempts < max_attempts:
                attempts += 1
                print(f"Checking stack status, attempt {attempts}/{max_attempts}...")
                
                check_cmd = f"aws cloudformation describe-stacks --stack-name {stack_name} {region_param}"
                check_result = subprocess.run(
                    check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                
                if check_result.returncode != 0:
                    # If stack description command fails, usually means the stack doesn't exist or there's a permission issue
                    if "Stack with id" in check_result.stderr and "does not exist" in check_result.stderr:
                        return f"Error: Stack '{stack_name}' was not created. Please check your AWS permissions and configuration."
                    return f"Error checking stack status:\n{check_result.stderr}"
                    
                try:
                    stack_info = json.loads(check_result.stdout)
                    if not stack_info.get("Stacks") or len(stack_info["Stacks"]) == 0:
                        return f"Error: Stack '{stack_name}' information could not be retrieved properly."
                    
                    status = stack_info["Stacks"][0]["StackStatus"]
                    print(f"Current stack status: {status}")
                    
                    # Check final status
                    if status.endswith("_COMPLETE"):
                        if status == "CREATE_COMPLETE" or status == "UPDATE_COMPLETE":
                            return "CloudFormation stack deployment succeeded."
                        else:
                            return f"Stack deployment completed with status: {status}"
                            
                    if status.endswith("_FAILED") or "ROLLBACK" in status:
                        # Get failure reason
                        reason = stack_info["Stacks"][0].get("StackStatusReason", "No reason provided")
                        return f"Stack deployment failed with status: {status}\nReason: {reason}"
                    
                    # Stack is still being created/updated, wait and check again
                    print(f"[INFO] Stack is in {status} state. Waiting...")
                    time.sleep(10)  # Wait 10 seconds before checking again
                    
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    return f"Error parsing stack status: {e}\nRaw output: {check_result.stdout[:200]}..."
                    
            return "CloudFormation stack deployment initiated, but final status could not be determined in the timeout period. Please check AWS console."

        except Exception as e:
            return f"Exception occurred during deployment:\n{e}"