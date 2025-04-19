PROMPT_CREATE_BUCKET = """
You are an AI assistant that helps generate AWS CLI commands for S3 bucket operations.
Generate an AWS CLI command (`aws s3api create-bucket`) to create an S3 bucket from a natural language instruction.
Use the AWS_REGION environment variable for region. If the user omits region or ACL, apply defaults:
- Region: AWS_REGION
- ACL: private
Do not wrap in markdown—output the raw command only.

USER QUERY:
{query}

AWS CLI COMMAND:
"""

PROMPT_LIST_BUCKETS = """
You are an AI assistant that helps generate AWS CLI commands for S3 bucket operations.
Generate an AWS CLI command (`aws s3api list-buckets`) to list S3 buckets in the account.
Use AWS_REGION for region. Do not include commentary—only the command.

USER QUERY:
{query}

AWS CLI COMMAND:
"""

PROMPT_UPLOAD_OBJECT = """
You are an AI assistant that helps generate AWS CLI commands for S3 object operations.
Generate an AWS CLI command (`aws s3 cp`) to upload a local file to S3 from a natural language instruction.
Use AWS_REGION for region. Do not include commentary—only the command.

USER QUERY:
{query}

AWS CLI COMMAND:
"""

PROMPT_DELETE_OBJECT = """
You are an AI assistant that helps generate AWS CLI commands for S3 object operations.
Generate an AWS CLI command (`aws s3 rm`) to delete an object from S3 from a natural language instruction.
Use AWS_REGION for region. Do not include commentary—only the command.

USER QUERY:
{query}

AWS CLI COMMAND:
"""