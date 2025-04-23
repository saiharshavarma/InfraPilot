import sys
from typing import Any
import readline


from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain.memory import ConversationBufferMemory
import colorama

from callbacks import handlers
from config import config
from i18n import text
from utils import utils
from agent.agent import create_agent
from k8s.toolkit import KubernetesToolKit

last_error = None


def get_llm(config):
    """Create and return the appropriate LLM based on configuration."""

    if config.infrapilot_CONFIG.model_provider == "openai":
        return ChatOpenAI(
            model_name=config.infrapilot_CONFIG.model_name,
            temperature=0,
            api_key=config.infrapilot_CONFIG.api_key,
            # callbacks=[handlers.PrintReasoningCallbackHandler()] if config.infrapilot_CONFIG.show_reasoning else None,
        )
    elif config.infrapilot_CONFIG.model_provider == "deepseek":
        return ChatDeepSeek(
            model_name=config.infrapilot_CONFIG.model_name,
            temperature=0,
            api_key=config.infrapilot_CONFIG.api_key,
        )
    else:
        supported_providers = ["openai", "deepseek"]
        raise ValueError(
            f"Unsupported model provider: {config.infrapilot_CONFIG.model_provider}. "
            f"Supported providers: {', '.join(supported_providers)}"
        )


def setup_agent() -> Any:
    config.init()
    colorama.init()

    llm = get_llm(config)
    text.init_system_messages(llm)
    memory = ConversationBufferMemory(memory_key="chat_history")

    enabled_toolkits = [
        toolkit.lower() for toolkit in config.infrapilot_CONFIG.toolkits
    ]

    tools = []
    if "kubernetes" in enabled_toolkits:
        kubernetes_toolkit = KubernetesToolKit(llm=llm)
        tools.extend(kubernetes_toolkit.get_tools())

        # Add AWS toolkit if both Kubernetes and AWS are enabled
        if "aws" in enabled_toolkits:
            from aws.toolkit import AWSToolKit

            aws_toolkit = AWSToolKit(llm=llm)
            tools.extend(aws_toolkit.get_tools())

    elif "aws" in enabled_toolkits:
        from aws.toolkit import AWSToolKit

        aws_toolkit = AWSToolKit(llm=llm)
        tools.extend(aws_toolkit.get_tools())

    elif "docker" in enabled_toolkits:
        from docker.toolkit import DockerToolKit

        docker_toolkit = DockerToolKit(llm=llm)
        tools.extend(docker_toolkit.get_tools())

    else:
        print(text.get("enable_no_toolkit"))
        sys.exit(1)

    return create_agent(
        llm,
        shared_memory=memory,
        tools=tools,
        verbose=config.infrapilot_CONFIG.verbose,
    )


def run():
    infrapilot_agent = setup_agent()

    print(text.get("welcome"))
    user_query = None
    while True:
        user_query = input(">")
        if utils.is_inform_sent():
            continue
        elif user_query == "exit":
            break
        elif user_query == "infrapilot_log":
            print_last_error()
            continue
        elif user_query.startswith("#"):
            continue
        elif not user_query.strip():
            continue

        try:
            result = infrapilot_agent.run(user_query)
        except handlers.HumanRejectedException as he:
            utils.print_rejected_message()
            continue
        except Exception as e:
            handle_exception(e)
            continue

        utils.print_ai_response(result)


def handle_exception(e):
    global last_error
    print(text.get("response_prefix"), end="")
    print(text.get("error_occur_message"))
    last_error = e


def print_last_error():
    if last_error is None:
        print(text.get("response_prefix"), end="")
        print(text.get("no_error_message"))
    else:
        print(last_error)
