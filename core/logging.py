import logging
import sys
import typing

import structlog
from core.config import conf
import orjson


def orjson_dumps(
        v,
        *,
        default: typing.Optional[typing.Callable[[typing.Any], typing.Any]] = None
) -> str:
    """Custom JSON serialization using orjson."""
    return orjson.dumps(v, default=default).decode()


def setup_logger() -> structlog.typing.FilteringBoundLogger:
    """
    Initializes and configures the logger with enhanced visual formatting
    for development and structured JSON formatting for production.
    """
    # Set up basic Python logging
    logging.basicConfig(
        level=conf.bot.logging_level,  # Log level from configuration
        stream=sys.stdout,  # Log output stream
        format="%(message)s",  # Simplified log format
    )

    # Shared processors for all environments
    shared_processors: list[structlog.typing.Processor] = [
        structlog.processors.add_log_level,  # Include log level in the log
        structlog.processors.TimeStamper(fmt="iso", utc=True),  # Add timestamp in ISO format
    ]

    # Define colored output for development
    def add_color(logger, method_name, event_dict):
        """
        Adds color to log levels for better visual distinction.
        """
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
        # Development-friendly processors with color and pretty output
        environment_processors = [
            add_color,  # Add color to log levels
            structlog.dev.ConsoleRenderer(pad_event=20),  # Nicely formatted console logs
        ]
    else:
        # Production-friendly processors with JSON formatting
        environment_processors = [
            structlog.processors.dict_tracebacks,  # Structured tracebacks
            structlog.processors.JSONRenderer(serializer=orjson_dumps),  # JSON logs
        ]

    # Combine shared and environment-specific processors
    processors = shared_processors + environment_processors

    # Configure structlog with the selected processors
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(conf.bot.logging_level),
        logger_factory=structlog.PrintLoggerFactory(),
    )

    # Return a logger instance
    return structlog.get_logger()
