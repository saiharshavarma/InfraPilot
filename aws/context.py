import os
import boto3

# Module-level AWS session and clients
_session = None
ec2_client = None
s3_client = None
dynamodb_client = None

def init_aws_session():
    global _session, ec2_client, cfn_client, s3_client, dynamodb_client
    if _session is None:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_session_token = os.getenv("AWS_SESSION_TOKEN")
        aws_region = os.getenv("AWS_REGION", "us-east-1")

        _session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=aws_region,
        )

        ec2_client = _session.client("ec2")
        s3_client = _session.client("s3")
        dynamodb_client = _session.client("dynamodb")