import logging
import sys
from langchain.schema.language_model import BaseLanguageModel

from docker import context
from docker.tools.container.tool import (
    RunContainerTool,
    StopContainerTool,
    RemoveContainerTool,
    ExecContainerTool,
    LogsContainerTool,
    ListContainersTool,
    InspectContainerTool,
)
from docker.tools.image.tool import (
    PullImageTool,
    BuildImageTool,
    RemoveImageTool,
    TagImageTool,
    PushImageTool,
    ListImagesTool,
    InspectImageTool,
)
from docker.tools.volume.tool import (
    CreateVolumeTool,
    RemoveVolumeTool,
    InspectVolumeTool,
    ListVolumesTool,
)

logger = logging.getLogger(__name__)


class DockerToolKit:
    """Docker toolkit for Infrapilot: provides container, image, and volume operations via LLM-driven tools."""

    llm: BaseLanguageModel

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.precheck()

    def precheck(self):
        """Check if Docker is available."""
        if not context.is_docker_available():
            print("Precheck failed: Docker not found or not running.")
            sys.exit(1)

    def get_tools(self):
        """Return the list of Docker tools exposed by this toolkit."""
        tools = [
            # Container tools
            RunContainerTool(llm=self.llm),
            StopContainerTool(llm=self.llm),
            RemoveContainerTool(llm=self.llm),
            ExecContainerTool(llm=self.llm),
            LogsContainerTool(llm=self.llm),
            ListContainersTool(),
            InspectContainerTool(),
            
            # Image tools
            PullImageTool(llm=self.llm),
            BuildImageTool(llm=self.llm),
            RemoveImageTool(llm=self.llm),
            TagImageTool(llm=self.llm),
            PushImageTool(llm=self.llm),
            ListImagesTool(),
            InspectImageTool(),
            
            # Volume tools
            CreateVolumeTool(llm=self.llm),
            RemoveVolumeTool(llm=self.llm),
            InspectVolumeTool(llm=self.llm),
            ListVolumesTool(),
        ]
        return tools