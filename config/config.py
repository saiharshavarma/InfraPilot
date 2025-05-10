import logging

import urllib3
from utils import utils

from pydantic import BaseModel
from dotenv import load_dotenv
import os


class Config(BaseModel):
    natural_language: str
    toolkits: list[str]
    show_reasoning: bool
    verbose: bool
    RAG_ENABLED: bool
    REMOTE_DOC_URLS: list[str]


infrapilot_CONFIG: Config


def init():
    load_dotenv()
    openai_api_base = utils.get_env("OPENAI_API_BASE")
    openai_api_key = utils.get_env("OPENAI_API_KEY")
    natural_language = utils.get_env("NATURAL_LANGUAGE", "English")
    toolkits = utils.get_env_list("TOOLKITS")
    show_reasoning = utils.get_env_bool("SHOW_REASONING", True)
    verbose = utils.get_env_bool("VERBOSE", False)
    RAG_ENABLED = utils.get_env_bool("RAG_ENABLED", False)
    FETCH_REMOTE_DOCS = utils.get_env_bool("FETCH_REMOTE_DOCS", False)
    REMOTE_DOC_URLS = (
        utils.get_env("REMOTE_DOC_URLS").split(",")
        if FETCH_REMOTE_DOCS else []
    )

    if not openai_api_key:
        raise Exception("OPENAI_API_KEY is not set")

    if not verbose:
        logging.basicConfig(level=logging.CRITICAL)
        # Disable child loggers of urllib3, e.g. urllib3.connectionpool
        logging.getLogger(urllib3.__package__).propagate = False

    global infrapilot_CONFIG
    infrapilot_CONFIG = Config(
        openai_api_base=openai_api_base,
        openai_api_key=openai_api_key,
        natural_language=natural_language,
        toolkits=toolkits,
        show_reasoning=show_reasoning,
        verbose=verbose,
        RAG_ENABLED=RAG_ENABLED,
        REMOTE_DOC_URLS=REMOTE_DOC_URLS
    )


def set_verbose(verbose: bool):
    global infrapilot_CONFIG
    infrapilot_CONFIG.verbose = verbose


def set_show_reasoning(show_reasoning: bool):
    global infrapilot_CONFIG
    infrapilot_CONFIG.show_reasoning = show_reasoning
