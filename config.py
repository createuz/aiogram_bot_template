import subprocess  # noqa: S404

from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
BOT_ID: str = BOT_TOKEN.split(":")[0]

LOGGING_LEVEL: int = os.getenv("LOGGING_LEVEL")

PG_HOST: str = os.getenv("PG_HOST")
PG_PORT: int = os.getenv("PG_PORT")
PG_USER: str = os.getenv("PG_USER")
PG_PASSWORD: str = os.getenv("PG_PASSWORD")
PG_DATABASE: str = os.getenv("PG_DATABASE")

FSM_HOST: str = os.getenv("FSM_HOST")
FSM_PORT: int = os.getenv("FSM_PORT")
FSM_PASSWORD: str = os.getenv("FSM_PASSWORD")
REDIS_URL: str = os.getenv("REDIS_URL")

USE_CACHE: bool = os.getenv("USE_CACHE")

if USE_CACHE:
    CACHE_HOST: str = os.getenv("CACHE_HOST")
    CACHE_PORT: int = os.getenv("CACHE_PORT")
    CACHE_PASSWORD: str = os.getenv("CACHE_PASSWORD")

USE_WEBHOOK: bool = os.getenv("USE_WEBHOOK")

if USE_WEBHOOK:
    MAIN_WEBHOOK_ADDRESS: str = os.getenv("MAIN_WEBHOOK_ADDRESS")
    MAIN_WEBHOOK_SECRET_TOKEN: str = os.getenv("MAIN_WEBHOOK_SECRET_TOKEN")
    WEBHOOK_URL: str = f'{MAIN_WEBHOOK_ADDRESS}/{BOT_TOKEN}'

    MAIN_WEBHOOK_LISTENING_HOST: str = os.getenv("MAIN_WEBHOOK_LISTENING_HOST")
    MAIN_WEBHOOK_LISTENING_PORT: int = 8443

    MAX_UPDATES_IN_QUEUE: int = os.getenv("MAX_UPDATES_IN_QUEUE")

USE_CUSTOM_API_SERVER: bool = os.getenv("USE_CUSTOM_API_SERVER")

if USE_CUSTOM_API_SERVER:
    CUSTOM_API_SERVER_IS_LOCAL: bool = os.getenv("CUSTOM_API_SERVER_IS_LOCAL")
    CUSTOM_API_SERVER_BASE: str = os.getenv("CUSTOM_API_SERVER_BASE")
    CUSTOM_API_SERVER_FILE: str = os.getenv("CUSTOM_API_SERVER_FILE")

DROP_PREVIOUS_UPDATES: bool = os.getenv("DROP_PREVIOUS_UPDATES")
