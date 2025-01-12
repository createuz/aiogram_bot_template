import logging
import sys
import typing
from typing import Optional

import orjson
import structlog.typing

from data.config import conf


def orjson_dumps(v, *, default: typing.Optional[typing.Callable[[typing.Any], typing.Any]] = None) -> Optional[str]:
    """Custom JSON serialization using orjson."""

    return orjson.dumps(v, default=default).decode()


def setup_logger() -> structlog.typing.FilteringBoundLogger:
    """
    Initializes and configures the logger with enhanced visual formatting
    for development and structured JSON formatting for production.
    """

    logging.basicConfig(level=conf.bot.logging_level, stream=sys.stdout, format="%(message)s")
    shared_processors: list[structlog.typing.Processor] = [
        structlog.processors.add_log_level, structlog.processors.TimeStamper(fmt="iso", utc=True)]

    def add_color(logger, method_name, event_dict):
        """Adds color to log levels for better visual distinction."""

        level = event_dict.get("level", "").upper()
        colors = {
            "DEBUG": "\033[94m",  # Blue
            "INFO": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "CRITICAL": "\033[41m",  # Red background
        }
        reset_color = "\033[0m"
        if level in colors:
            event_dict["level"] = f"{colors[level]}{level}{reset_color}"
        return event_dict

    if sys.stderr.isatty():
        environment_processors = [add_color, structlog.dev.ConsoleRenderer(pad_event=20)]
    else:
        environment_processors = [
            structlog.processors.dict_tracebacks, structlog.processors.JSONRenderer(serializer=orjson_dumps)]
    processors = shared_processors + environment_processors
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(conf.bot.logging_level),
        logger_factory=structlog.PrintLoggerFactory(),
    )
    return structlog.get_logger()