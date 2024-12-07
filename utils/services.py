import logging

import asyncpg
import redis
import structlog
import tenacity
from redis.asyncio import ConnectionPool, Redis
from tenacity import _utils  # noqa: PLC2701

TIMEOUT_BETWEEN_ATTEMPTS = 2
MAX_TIMEOUT = 30
def before_log(retry_state: tenacity.RetryCallState) -> None:
    """
    Log information about retry attempts before they are executed.
    """
    if retry_state.outcome is None:
        return

    # Determine the outcome type and corresponding message
    if retry_state.outcome.failed:
        verb, value = "raised", retry_state.outcome.exception()
    else:
        verb, value = "returned", retry_state.outcome.result()

    # Extract logger from kwargs, with a fallback if not provided
    logger = retry_state.kwargs.get("logger", logging.getLogger(__name__))

    # Log retry information with structured context for better debugging
    logger.info(
        f"Retrying '{_utils.get_callback_name(retry_state.fn)}' in {retry_state.next_action.sleep} seconds "
        f"as it {verb} {value}",
        extra={
            "callback": _utils.get_callback_name(retry_state.fn),
            "sleep": retry_state.next_action.sleep,
            "verb": verb,
            "value": str(value),  # Ensure value is string-safe
            "attempt_number": retry_state.attempt_number,
        },
    )



def after_log(retry_state: tenacity.RetryCallState) -> None:
    """
    Log information after a retryable function has been executed.
    """
    # Extract logger from kwargs, with a fallback if not provided
    logger = retry_state.kwargs.get("logger", logging.getLogger(__name__))

    # Log completion information with structured context for better debugging
    logger.info(
        f"Finished call to '{_utils.get_callback_name(retry_state.fn)}' "
        f"after {retry_state.seconds_since_start:.2f} seconds. "
        f"This was the {_utils.to_ordinal(retry_state.attempt_number)} attempt.",
        extra={
            "callback": _utils.get_callback_name(retry_state.fn),
            "time": retry_state.seconds_since_start,
            "attempt": _utils.to_ordinal(retry_state.attempt_number),
        },
    )


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before_sleep=before_log,
    after=after_log,
)
async def wait_postgres(
    logger: structlog.typing.FilteringBoundLogger,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> asyncpg.Pool:
    db_pool = await asyncpg.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        min_size=1,
        max_size=3
    )
    version = await db_pool.fetchrow("SELECT version() as ver;")
    logger.debug("Connected to PostgreSQL.", version=version["ver"])
    return db_pool


@tenacity.retry(
    wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
    stop=tenacity.stop_after_delay(MAX_TIMEOUT),
    before_sleep=before_log,
    after=after_log,
)
async def wait_redis_pool(
    logger: structlog.typing.FilteringBoundLogger,
    host: str,
    port: int,
    password: str,
    database: int,
) -> redis.asyncio.Redis:  # type: ignore[type-arg]
    redis_pool: redis.asyncio.Redis = Redis(  # type: ignore[type-arg]
        connection_pool=ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=database,
        )
    )
    version = await redis_pool.info("server")
    logger.debug("Connected to Redis.", version=version["redis_version"])
    return redis_pool
