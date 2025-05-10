from langchain.schema.language_model import BaseLanguageModel
from .context import init_aws_session, ec2_client, s3_client, dynamodb_client
from .tools.ec2.tool import (
    CreateEC2InstanceTool,
    TerminateEC2InstanceTool,
    ModifyEC2InstancesTool,
)
from .tools.s3.tool import (
    CreateS3BucketTool,
    ListS3BucketsTool,
    UploadS3ObjectTool,
    DeleteS3ObjectTool,

)
from .tools.dynamodb.tool import (
    CreateDynamoDBTableTool,
    PutDynamoDBItemTool,
    GetDynamoDBItemTool,
)
from .tools.cloudformation.tool import (
    GenerateCloudFormationTemplateTool,
    DeployCloudFormationStackTool,
    ListCloudFormationStacksTool,
)
from .tools.cloudformation.delete_tool import DeleteCloudFormationStackTool

class AWSToolKit:
    """AWS toolkit for Infrapilot: provides EC2, S3 and DynamoDB operations via LLM-driven tools."""

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        init_aws_session()

    def get_tools(self):
        """Return the list of AWS tools exposed by this toolkit."""
        return [
            # EC2
            CreateEC2InstanceTool(llm=self.llm, ec2_client=ec2_client),
            TerminateEC2InstanceTool(llm=self.llm, ec2_client=ec2_client),
            ModifyEC2InstancesTool(llm=self.llm, ec2_client=ec2_client),
            # S3
            CreateS3BucketTool(llm=self.llm, s3_client=s3_client),
            ListS3BucketsTool(llm=self.llm, s3_client=s3_client),
            UploadS3ObjectTool(llm=self.llm, s3_client=s3_client),
            DeleteS3ObjectTool(llm=self.llm, s3_client=s3_client),

            # DynamoDB
            CreateDynamoDBTableTool(llm=self.llm, dynamodb_client=dynamodb_client),
            PutDynamoDBItemTool(llm=self.llm, dynamodb_client=dynamodb_client),
            GetDynamoDBItemTool(llm=self.llm, dynamodb_client=dynamodb_client),
            # CloudFormation
            GenerateCloudFormationTemplateTool(llm=self.llm),
            DeployCloudFormationStackTool(llm=self.llm),
            DeleteCloudFormationStackTool(llm=self.llm),
            ListCloudFormationStacksTool(llm=self.llm),
        ]