import logging as log
import sys
from typing import Optional, Callable, Any

import orjson
import structlog
from structlog.typing import FilteringBoundLogger, Processor

from data.config import conf


def orjson_dumps(v, *, default: Optional[Callable[[Any], Any]] = None) -> Optional[str]:
    return orjson.dumps(v, default=default).decode()


def setup_logger() -> FilteringBoundLogger:
    import logging
    logging.basicConfig(
        level=conf.bot_token.logging_level, stream=sys.stdout,
        format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s'
    )
    shared_processors: list[Processor] = [
        structlog.processors.add_log_level, structlog.processors.TimeStamper(fmt="iso", utc=True)]

    def add_color(logger, method_name, event_dict):
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
        processors=processors, wrapper_class=structlog.make_filtering_bound_logger(conf.bot_token.logging_level),
        logger_factory=structlog.PrintLoggerFactory()
    )
    return structlog.get_logger()


log.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=log.INFO)
logger = log.getLogger(__name__)
