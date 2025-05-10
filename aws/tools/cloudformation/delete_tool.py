import subprocess
import re
import os
import json
import time
from langchain.schema.language_model import BaseLanguageModel
from langchain.agents.tools import BaseTool

class DeleteCloudFormationStackTool(BaseTool):
    name = "delete_cloudformation_stack"
    description = (
        "Delete a CloudFormation stack using AWS CLI based on a natural language query. "
        "You must provide the stack name. Region defaults to us-east-1 unless specified."
    )
    llm: BaseLanguageModel

    def _run(self, query: str) -> str:
        print(f"\n===== DELETE STACK TOOL: STARTING =====")
        print(f"Query received: {query}")
        
        # --- STEP 1: Check if input is JSON ---
        stack_name = None
        region = os.getenv("AWS_REGION", "us-east-1")
        
        # Try to parse as JSON first
        try:
            json_input = json.loads(query)
            if isinstance(json_input, dict):
                # Check for stack_name field in JSON
                if "stack_name" in json_input:
                    stack_name = json_input["stack_name"]
                    print(f"Stack name found in JSON: {stack_name}")
                
                # Check for region field in JSON
                if "region" in json_input:
                    region = json_input["region"]
                    print(f"Region found in JSON: {region}")
        except (json.JSONDecodeError, TypeError):
            # Not JSON, continue with text parsing
            print("Input is not valid JSON, proceeding with text extraction")
        
        # --- STEP 2: Extract stack name from text if not found in JSON ---
        if not stack_name:
            # Try explicit pattern first
            explicit_match = re.search(r"stack[-\s_]?name[\s:]+['\"]?([a-zA-Z0-9-_]+)['\"]?", query, re.IGNORECASE)
            if explicit_match:
                stack_name = explicit_match.group(1)
                print(f"Stack name found via explicit pattern: {stack_name}")
            
            # Try simpler patterns if explicit one fails
            if not stack_name:
                # Look for words following "delete" or "remove"
                action_match = re.search(r"(?:delete|remove)(?:\s+the)?\s+(?:stack\s+)?['\"]*([a-zA-Z0-9-_]+)['\"]*", query, re.IGNORECASE)
                if action_match:
                    stack_name = action_match.group(1)
                    print(f"Stack name found via action pattern: {stack_name}")
            
            # Fallback: Just look for alphanumeric strings that could be stack names
            if not stack_name:
                # Look for any words that might be stack names - this is prone to false positives but a last resort
                possible_names = re.findall(r"[a-zA-Z][\w-]+", query)
                if possible_names:
                    # Filter out common words that are definitely not stack names
                    common_words = ["stack", "delete", "region", "aws", "cloudformation", "the", "and", "this", "that"]
                    filtered_names = [n for n in possible_names if n.lower() not in common_words and len(n) > 2]
                    if filtered_names:
                        stack_name = filtered_names[0]  # Use the first potential stack name
                        print(f"Stack name found via fallback pattern: {stack_name}")
        
        if not stack_name:
            return "ERROR: Could not identify a stack name in your query. Please specify the stack name explicitly (e.g., 'delete stack MyStackName')."
        
        # --- STEP 3: Extract region from text if not found in JSON ---
        if not region or region == "us-east-1":  # Only look in text if region wasn't found in JSON or is the default
            region_match = re.search(r"region[\s:]+['\"]?([a-z0-9-]+)['\"]?", query, re.IGNORECASE)
            if region_match:
                region = region_match.group(1)
        
        print(f"Using region: {region}")
        
        # --- STEP 4: Get all available stacks for debugging ---
        print("\n----- Listing available stacks -----")
        list_cmd = f"aws cloudformation list-stacks --region {region}"
        list_result = subprocess.run(list_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        available_stacks = []
        similar_stacks = []
        
        if list_result.returncode == 0:
            try:
                data = json.loads(list_result.stdout)
                available_stacks = [s["StackName"] for s in data.get("StackSummaries", [])]
                print(f"All stacks found ({len(available_stacks)}): {available_stacks}")
                
                # Check if our stack is in the list
                if stack_name in available_stacks:
                    print(f"EXACT MATCH FOUND for {stack_name}")
                else:
                    print(f"WARNING: No exact match found for {stack_name}")
                    
                    # Find similar names for helpful error messages
                    for s in available_stacks:
                        # Check for similarity
                        if stack_name.lower() in s.lower() or s.lower() in stack_name.lower():
                            similar_stacks.append(s)
                    
                    if similar_stacks:
                        print(f"Similar stack names found: {similar_stacks}")
                        # If we found similar stacks, use the closest one
                        closest = min(similar_stacks, key=lambda x: abs(len(x) - len(stack_name)))
                        print(f"Using closest match: {closest} instead of {stack_name}")
                        stack_name = closest
            except Exception as e:
                print(f"WARNING: Error parsing stack list: {str(e)}")
        else:
            print(f"WARNING: Could not list stacks: {list_result.stderr}")
        
        # --- STEP 5: Verify stack exists ---
        print(f"\n----- Checking if stack '{stack_name}' exists -----")
        describe_cmd = f"aws cloudformation describe-stacks --stack-name {stack_name} --region {region}"
        describe_result = subprocess.run(describe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if describe_result.returncode != 0:
            print(f"Stack verification failed: {describe_result.stderr}")
            
            # Checks if the stack doesn't exist
            if "does not exist" in describe_result.stderr:
                error_msg = f"ERROR: Stack '{stack_name}' does not exist in region '{region}'."
                
                if similar_stacks:
                    error_msg += f" Did you mean one of these: {', '.join(similar_stacks)}?"
                    
                if available_stacks:
                    error_msg += f"\n\nAvailable stacks in region {region}:\n" + "\n".join(available_stacks)
                
                return error_msg
            
            return f"ERROR checking stack: {describe_result.stderr}"
        
        # Parse status for logging and verification
        try:
            data = json.loads(describe_result.stdout)
            status = data["Stacks"][0]["StackStatus"]
            print(f"Stack '{stack_name}' exists with status: {status}")
        except Exception as e:
            print(f"WARNING: Error parsing stack status: {e}")
        
        # --- STEP 6: Execute delete ---
        print(f"\n----- Deleting stack '{stack_name}' -----")
        delete_cmd = f"aws cloudformation delete-stack --stack-name {stack_name} --region {region}"
        delete_result = subprocess.run(delete_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if delete_result.returncode == 0:
            print(f"Delete command successful: {delete_result.stdout}")
            return f"SUCCESS: Deletion of stack '{stack_name}' initiated successfully in region '{region}'."
        else:
            print(f"Delete command failed: {delete_result.stderr}")
            return f"ERROR deleting stack '{stack_name}':\n{delete_result.stderr}"