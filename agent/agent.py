from typing import Any, Dict, Optional

from langchain.tools import Tool
from langchain.tools import BaseTool
from langchain.agents.agent import AgentExecutor
from langchain.agents.conversational.base import ConversationalAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.memory import ReadOnlySharedMemory
from langchain.schema.language_model import BaseLanguageModel

from config import config
from tools.human.tool import HumanTool
from tools.reasoning.tool import ShowReasoningTool, HideReasoningTool
from agent.output_parser import OutputParser
from agent.prompt import (
    AGENT_PROMPT_PREFIX,
    FORMAT_INSTRUCTIONS_TEMPLATE,
)


def create_agent(
    llm: BaseLanguageModel,
    shared_memory: Optional[ReadOnlySharedMemory] = None,
    tools: list[BaseTool] = [],
    callback_manager: Optional[BaseCallbackManager] = None,
    verbose: bool = True,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Dict[str, Any],
) -> AgentExecutor:
    """Instantiate planner for a given task."""

    system_tools = [
        HumanTool(),
        ShowReasoningTool(),
        HideReasoningTool(),
    ]

    tools.extend(system_tools)

    if config.infrapilot_CONFIG.RAG_ENABLED:
        from rag.ingest import ingest_documentation
        ingest_documentation(source_dir="docs")
        from rag.rag_chain import create_rag_chain
        rag_chain = create_rag_chain(k=3)
        docs_tool = Tool(
            name="documentation_search",
            func=lambda q: rag_chain.run(q),
            description="Retrieve up-to-date Kubernetes/AWS documentation snippets"
        )
        tools.append(docs_tool)

    format_instructions = FORMAT_INSTRUCTIONS_TEMPLATE.format(
        natural_language=config.infrapilot_CONFIG.natural_language
    )
    prompt = ConversationalAgent.create_prompt(
        tools,
        prefix=AGENT_PROMPT_PREFIX,
        format_instructions=format_instructions,
    )

    agent = ConversationalAgent(
        llm_chain=LLMChain(
            llm=llm, prompt=prompt, verbose=config.infrapilot_CONFIG.verbose
        ),
        output_parser=OutputParser(),
        allowed_tools=[tool.name for tool in tools],
        **kwargs,
    )

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=shared_memory,
        callback_manager=callback_manager,
        verbose=verbose,
        **(agent_executor_kwargs or {}),
    )
