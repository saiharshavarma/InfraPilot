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

        raw = self.llm.predict(
            PROMPT_DEPLOY_CLOUDFORMATION_STACK.format(query=query)
        ).strip()

        # 清除 markdown 格式的包裹行
        lines = raw.strip().splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
            if lines and lines[-1].strip().endswith("```"):
                lines = lines[:-1]
        cmd = "\n".join(lines).strip()

        print("Generated AWS CLI command:", cmd)
        
        # 从命令中提取stack-name参数
        stack_name_match = re.search(r'--stack-name\s+(\S+)', cmd)
        if not stack_name_match:
            return "Error: Could not find stack name in the command."
        
        stack_name = stack_name_match.group(1)
        
        # 从命令中提取region参数，如果有的话
        region_match = re.search(r'--region\s+(\S+)', cmd)
        region_param = f"--region {region_match.group(1)}" if region_match else ""

        try:
            result = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # 检查是否有成功信息
            if result.returncode == 0:
                return "CloudFormation stack deployment succeeded."

            # 检查一些特定的成功情况
            if "No changes to deploy" in result.stderr:
                return "Stack is already up-to-date. No changes were made."
                
            # 提取stack-name和region（如果有）
            stack_name_match = re.search(r'--stack-name\s+(\S+)', cmd)
            if stack_name_match:
                stack_name = stack_name_match.group(1)
                region_match = re.search(r'--region\s+(\S+)', cmd)
                region_param = f"--region {region_match.group(1)}" if region_match else ""
                
                # 检查栈是否实际存在
                check_cmd = f"aws cloudformation describe-stacks --stack-name {stack_name} {region_param}"
                check_result = subprocess.run(
                    check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                
                if check_result.returncode == 0:
                    # 栈确实存在，部署可能已经成功
                    return "CloudFormation stack exists despite reported errors. Deployment appears to be successful."
            return f"Error during deployment:\n{result.stderr}"
            # 部署命令成功，等待栈创建完成
            max_attempts = 5
            attempts = 0
            while attempts < max_attempts:
                attempts += 1
                check_cmd = f"aws cloudformation describe-stacks --stack-name {stack_name} {region_param}"
                check_result = subprocess.run(
                    check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                
                if check_result.returncode != 0:
                    return f"Error checking stack status:\n{check_result.stderr}"
                    
                try:
                    stack_info = json.loads(check_result.stdout)
                    status = stack_info["Stacks"][0]["StackStatus"]
                    
                    if status.endswith("_COMPLETE"):
                        if status == "CREATE_COMPLETE" or status == "UPDATE_COMPLETE":
                            return "CloudFormation stack deployment succeeded."
                        else:
                            return f"Stack deployment completed with status: {status}"
                            
                    if status.endswith("_FAILED"):
                        return f"Stack deployment failed with status: {status}"
                        
                    # 栈仍在创建中，等待并再次检查
                    print(f"Stack is in {status} state. Waiting...")
                    time.sleep(10)  # 等待10秒后再检查
                    
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    return f"Error parsing stack status: {e}"
                    
            return "CloudFormation stack deployment initiated, but final status could not be determined in the timeout period. Please check AWS console."

        except Exception as e:
            return f"Exception occurred:\n{e}"