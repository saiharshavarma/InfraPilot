import logging

import urllib3
from utils import utils

from pydantic import BaseModel
from dotenv import load_dotenv


class Config(BaseModel):
    api_key: str
    api_base: str
    model_provider: str  # 新增模型提供商字段
    model_name: str  # 新增模型名称字段
    natural_language: str
    toolkits: list[str]
    show_reasoning: bool
    verbose: bool


infrapilot_CONFIG: Config


def init():
    load_dotenv()
    model_provider = utils.get_env(
        "MODEL_PROVIDER", "deepseek"
    )
    api_base = utils.get_env(
        "API_BASE", "https://api.deepseek.com/v1"
    )
    api_key = utils.get_env("API_KEY")
    model_name = utils.get_env(
        "MODEL_NAME", "deepseek-chat"
    )
    natural_language = utils.get_env("NATURAL_LANGUAGE", "English")
    toolkits = utils.get_env_list("TOOLKITS")
    show_reasoning = utils.get_env_bool("SHOW_REASONING", True)
    verbose = utils.get_env_bool("VERBOSE", False)

    if not api_key:
        raise Exception("API_KEY is not set")

    if not verbose:
        logging.basicConfig(level=logging.CRITICAL)
        # Disable child loggers of urllib3, e.g. urllib3.connectionpool
        logging.getLogger(urllib3.__package__).propagate = False

    global infrapilot_CONFIG
    infrapilot_CONFIG = Config(
        api_key=api_key,
        api_base=api_base,
        model_provider=model_provider,
        model_name=model_name,
        natural_language=natural_language,
        toolkits=toolkits,
        show_reasoning=show_reasoning,
        verbose=verbose,
    )


def set_verbose(verbose: bool):
    global infrapilot_CONFIG
    infrapilot_CONFIG.verbose = verbose


def set_show_reasoning(show_reasoning: bool):
    global infrapilot_CONFIG
    infrapilot_CONFIG.show_reasoning = show_reasoning
