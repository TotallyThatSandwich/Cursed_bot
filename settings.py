from dotenv import load_dotenv
from logging.config import dictConfig
import logging
import os
import json

load_dotenv()

TOKEN = os.getenv("TOKEN") 
BLACKLIST = os.getenv("BLACKLIST")
GENERAL = os.getenv("GENERAL")
GCYTC = os.getenv("GCYTC")
DEV = os.getenv("DEV")
GITHUB_REPO_URL = os.environ.get("GITHUB_REPO_URL")
GITHUB_PAT = os.environ.get("GITHUB_PAT")
VALORANT_KEY = os.environ.get("VALORANT_KEY")
STEAM_KEY = os.environ.get("STEAM_KEY")
BOT_IDS = os.environ.get("BOT_IDs")

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)