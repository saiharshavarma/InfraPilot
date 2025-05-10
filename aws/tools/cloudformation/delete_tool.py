import subprocess
import re
import os
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool

class DeleteCloudFormationStackTool(BaseTool):
    name = "delete_cloudformation_stack"
    description = (
        "Delete a CloudFormation stack using AWS CLI based on a natural language query. "
        "You must provide the stack name. Region will default to us-east-1 unless overridden."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        # Extract stack name from the query
        stack_match = re.search(r"stack[-\s_]?name[\s:]+['\"]?([a-zA-Z0-9-]+)['\"]?", query, re.IGNORECASE)
        if not stack_match:
            return "Error: No stack name found in the query. Please specify a stack name."
        
        stack_name = stack_match.group(1)
        
        # Extract region if provided
        region_match = re.search(r"region[\s:]+['\"]?([a-z0-9-]+)['\"]?", query, re.IGNORECASE)
        region = region_match.group(1) if region_match else os.getenv("AWS_REGION", "us-east-1")
        
        # Construct the command
        cmd = f"aws cloudformation delete-stack --stack-name {stack_name} --region {region}"
        print("Generated delete-stack command:", cmd)

        try:
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            if result.returncode == 0:
                return f"Stack '{stack_name}' deletion initiated."
            else:
                return f"Error deleting stack '{stack_name}': {result.stderr.strip()}"
        except Exception as e:
            return f"Exception occurred during stack deletion: {e}"