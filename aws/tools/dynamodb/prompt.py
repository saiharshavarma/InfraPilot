PROMPT_CREATE_TABLE = """
You are an AI assistant that helps generate AWS CLI commands for DynamoDB operations.
Generate an AWS CLI command (`aws dynamodb create-table`) to create a DynamoDB table from a natural language instruction.
Use AWS_REGION environment variable for region. Do not include commentary—only the command.

USER QUERY:
{query}

AWS CLI COMMAND:
"""

PROMPT_PUT_ITEM = """
You are an AI assistant that helps generate AWS CLI commands for DynamoDB operations.
Generate an AWS CLI command (`aws dynamodb put-item`) to insert an item into a DynamoDB table based on a natural language instruction.
Use AWS_REGION environment variable for region. Do not include commentary—only the command.

USER QUERY:
{query}

AWS CLI COMMAND:
"""

PROMPT_GET_ITEM = """
You are an AI assistant that helps generate AWS CLI commands for DynamoDB operations.
Generate an AWS CLI command (`aws dynamodb get-item`) to fetch an item from a DynamoDB table based on a natural language instruction.
Use AWS_REGION environment variable for region. Do not include commentary—only the command.

USER QUERY:
{query}

AWS CLI COMMAND:
"""